import Network
import argparse
import time
import hashlib


class Packet:
    ## the number of bytes used to store packet length
    seq_num_S_length = 10
    length_S_length = 10
    ack_S_length = 1
    ## length of md5 checksum in hex
    checksum_length = 32

    def __init__(self, seq_num, msg_S, ack = "A"):
        self.seq_num = seq_num
        self.msg_S = msg_S
        self.ack = ack

    @classmethod
    def from_byte_S(self, byte_S):
        if Packet.corrupt(byte_S):
            raise RuntimeError('Cannot initialize Packet: byte_S is corrupt')
        #extract the fields
        seq_num = int(byte_S[Packet.length_S_length : Packet.length_S_length+Packet.seq_num_S_length])
        ack = byte_S[Packet.length_S_length+Packet.length_S_length+Packet.seq_num_S_length+Packet.ack_S_length]
        msg_S = byte_S[Packet.length_S_length+Packet.seq_num_S_length+Packet.ack_S_length+Packet.checksum_length :]
        return self(seq_num, msg_S, ack)


    def get_byte_S(self):
        #convert sequence number of a byte field of seq_num_S_length bytes
        seq_num_S = str(self.seq_num).zfill(self.seq_num_S_length)
        #convert flags number of byte field of ack_num_S_length bytes
        ack_S = str(self.ack).zfill(self.ack_S_length)
        #convert length to a byte field of length_S_length bytes
        length_S = str(self.length_S_length + len(seq_num_S) + self.checksum_length + len(self.msg_S) + self.ack_S_length).zfill(self.length_S_length)
        #compute the checksum
        checksum = hashlib.md5((length_S+seq_num_S+self.ack+self.msg_S).encode('utf-8'))
        checksum_S = checksum.hexdigest()
        #compile into a string
        return length_S + seq_num_S + ack_S + checksum_S + self.msg_S

    @classmethod
    def get_ack(self, byte_S):
        before_ack = Packet.length_S_length + Packet.seq_num_S_length
        if byte_S[before_ack : before_ack + Packet.ack_S_length] == 'A':
            return True
        else:
            return False

    @staticmethod
    def corrupt(byte_S):
        #extract the fields
        length_S = byte_S[0 : Packet.length_S_length]
        seq_num_S = byte_S[Packet.length_S_length : Packet.seq_num_S_length+Packet.seq_num_S_length]
        ack_S = byte_S[Packet.length_S_length + Packet.seq_num_S_length:Packet.length_S_length + Packet.seq_num_S_length + Packet.ack_S_length]
        checksum_S = byte_S[Packet.seq_num_S_length+Packet.seq_num_S_length + Packet.ack_S_length: Packet.seq_num_S_length + Packet.length_S_length + Packet.ack_S_length + Packet.checksum_length]
        msg_S = byte_S[Packet.length_S_length+Packet.seq_num_S_length+Packet.ack_S_length+Packet.checksum_length :]

        #compute the checksum locally
        checksum = hashlib.md5(str(length_S+seq_num_S+ack_S+msg_S).encode('utf-8'))
        computed_checksum_S = checksum.hexdigest()
        #and check if the same
        return checksum_S != computed_checksum_S


class RDT:
    ## latest sequence number used in a packet
    seq_num = 1
    ## buffer of bytes read from network
    byte_buffer = ''

    def __init__(self, role_S, server_S, port):
        self.network = Network.NetworkLayer(role_S, server_S, port)

    def disconnect(self):
        self.network.disconnect()

    def rdt_1_0_send(self, msg_S):
        p = Packet(self.seq_num, msg_S)
        self.seq_num += 1
        self.network.udt_send(p.get_byte_S())

    def rdt_1_0_receive(self):
        ret_S = None
        byte_S = self.network.udt_receive()
        self.byte_buffer += byte_S
        #keep extracting packets - if reordered, could get more than one
        while True:
            #check if we have received enough bytes
            if(len(self.byte_buffer) < Packet.length_S_length):
                return ret_S #not enough bytes to read packet length
            #extract length of packet
            length = int(self.byte_buffer[:Packet.length_S_length])
            if len(self.byte_buffer) < length:
                return ret_S #not enough bytes to read the whole packet
            #create packet from buffer content and add to return string
            p = Packet.from_byte_S(self.byte_buffer[0:length])
            ret_S = p.msg_S if (ret_S is None) else ret_S + p.msg_S
            #remove the packet bytes from the buffer
            self.byte_buffer = self.byte_buffer[length:]
            #if this was the last packet, will return on the next iteration


    def rdt_2_1_send(self, msg_S):
        p = Packet(self.seq_num, msg_S)
        self.seq_num += 1
        self.network.udt_send(p.get_byte_S())
        #wait for an ack, if false, nack receieved, resend packet
        while not self.ack_receive(False):
            self.network.udt_send(p.get_byte_S())

    def rdt_2_1_receive(self):
        ret_S = None
        self.byte_buffer += self.network.udt_receive()

        while True:
            if len(self.byte_buffer) < Packet.length_S_length:
                return ret_S

            length = int(self.byte_buffer[:Packet.length_S_length])
            if len(self.byte_buffer) < length:
                return ret_S

            try:
                p = Packet.from_byte_S(self.byte_buffer[:length])
                ret_S = p.msg_S if ret_S is None else ret_s + p.msg_S

                self.ack_send(True)
            except RuntimeError:
                self.ack_send(False)

            self.byte_buffer = self.byte_buffer[length:]

    def ack_receive(self, wto):
        st = time.time()
        to = 0.5
        while True:
            if wto and st + to < time.time():
                return False
            #Keep collecting bytes
            self.byte_buffer += self.network.udt_receive()
            #Do we have enough bytes to grab the length of the incoming packet
            if len(self.byte_buffer) < Packet.length_S_length:
                continue

            length = int(self.byte_buffer[:Packet.length_S_length])
            if len(self.byte_buffer) < length:
                continue

            ack = Packet.get_ack(self.byte_buffer[:length])
            self.byte_buffer = self.byte_buffer[length:]
            return ack

    def ack_send(self, valid):
        p = Packet(self.seq_num, '', 'A' if valid else 'N')
        self.network.udt_send(p.get_byte_S())


    def rdt_3_0_send(self, msg_S):
        p = Packet(self.seq_num, msg_S)
        self.seq_num += 1
        self.network.udt_send(p.get_byte_S())
        #wait for an ack, if false, nack receieved, resend packet
        while not self.ack_receive(True):
            self.network.udt_send(p.get_byte_S())


    def rdt_3_0_receive(self):
        ret_S = None
        self.byte_buffer += self.network.udt_receive()

        st = time.time()
        to = 0.5
        while True:
            if st + to < time.time():
                self.byte_buffer = ''
                self.ack_send(False)
                return None

            if len(self.byte_buffer) < Packet.length_S_length:
                return ret_S

            length = int(self.byte_buffer[:Packet.length_S_length])
            if len(self.byte_buffer) < length:
                return ret_S

            try:
                p = Packet.from_byte_S(self.byte_buffer[:length])
                ret_S = p.msg_S if ret_S is None else ret_s + p.msg_S

                self.ack_send(True)
            except RuntimeError:
                self.ack_send(False)

            self.byte_buffer = self.byte_buffer[length:]

if __name__ == '__main__':
    parser =  argparse.ArgumentParser(description='RDT implementation.')
    parser.add_argument('role', help='Role is either client or server.', choices=['client', 'server'])
    parser.add_argument('server', help='Server.')
    parser.add_argument('port', help='Port.', type=int)
    args = parser.parse_args()

    rdt = RDT(args.role, args.server, args.port)
    if args.role == 'client':
        # rdt.rdt_1_0_send('MSG_FROM_CLIENT')
        # sleep(2)
        # print(rdt.rdt_1_0_receive())
        rdt.rdt_2_1_send('MSG_FROM_CLIENT')
        sleep(2)
        print(rdt.rdt_2_1_receive())
        rdt.disconnect()


    else:
        # sleep(1)
        # print(rdt.rdt_1_0_receive())
        # rdt.rdt_1_0_send('MSG_FROM_SERVER')
        sleep(1)
        print(rdt.rdt_2_1_receive())
        rdt.rdt_2_1_send('MSG_FROM_SERVER')
        rdt.disconnect()





