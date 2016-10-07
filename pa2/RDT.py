import Network
import argparse
from time import sleep
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
        ack = byte_S[Packet.length_S_length+Packet.seq_num_S_length:Packet.length_S_length+Packet.seq_num_S_length+Packet.ack_S_length]
        if ack == 'A':
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
        if self.ack_receive():
            self.network.udt_send(p.get_byte_S())


    #Some serious WIP
    def rdt_2_1_receive(self):
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
            try:
                p = Packet.from_byte_S(self.byte_buffer[0:length])
                ret_S = p.msg_S if (ret_S is None) else ret_S + p.msg_S
                self.ack_send(p.msg_S)
            except RuntimeError:
                self.nack_send()

            #remove the packet bytes from the buffer
            self.byte_buffer = self.byte_buffer[length:]
            #if this was the last packet, will return on the next iteration


    #Some serious WIP
    def ack_receive(self):
        ret_S = None
        byte_S = self.network.udt_receive()
        self.byte_buffer += byte_S
        while True:
            if len(self.byte_buffer) < Packet.length_S_length+Packet.seq_num_S_length+Packet.ack_S_length:
                return ret_S
            ack = Packet.get_ack(byte_buffer[:Packet.length_S_length+Packet.seq_num_S_length+Packet.ack_S_length])
            self.byte_buffer = self.byte_buffer[Packet.length_S_length+Packet.seq_num_S_length+Packet.ack_S_length:]

    def ack_send(self, msg_S):
        p = Packet(self.seq_num, msg_S, 'A')
        self.network.udt_send(p.get_byte_S())

    def nack_send(self):
        print("sending nack")
        p = Packet(self.seq_num, 'N')
        self.network.udt_send(p.get_byte_S())

    def rdt_3_0_send(self, msg_S):
        pass

    def rdt_3_0_receive(self):
        pass


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




