'''
Created on Oct 12, 2016

@author: mwitt_000
'''
import queue
import threading
from operator import itemgetter

## wrapper class for a queue of packets
class Interface:
    ## @param maxsize - the maximum size of the queue storing packets
    #  @param cost - of the interface used in routing
    def __init__(self, cost=0, maxsize=0, capacity=500):
        self.in_queue_0 = queue.Queue(maxsize);
        self.in_queue_1 = queue.Queue(maxsize);
        self.out_queue_0 = queue.Queue(maxsize);
        self.out_queue_1 = queue.Queue(maxsize);

        self.cost = cost
        self.capacity = capacity #serialization rate
        self.next_avail_time = 0 #The next time a packet can transmit

    ##get packet from the queue interface
    # @param in_or_out - use 'in' or 'out' interface
    def get(self, in_or_out):
        try:
            if in_or_out == 'in':
                # print('getting packet from the IN queue') #:-)
                if not self.in_queue_1.empty():
                    pkt_S = self.in_queue_1.get(False)
                else:
                    pkt_S = self.in_queue_0.get(False)
            else:
                # print('getting packet from the OUT queue') #:-)
                if not self.out_queue_1.empty():
                    pkt_S = self.out_queue_1.get(False)
                else:
                    pkt_S = self.out_queue_0.get(False)

            return pkt_S
        except queue.Empty:
            # print(in_or_out + ' - Both priorities empty') #:-)
            return None

    ##put the packet into the interface queue
    # @param pkt - Packet to be inserted into the queue
    # @param in_or_out - use 'in' or 'out' interface
    # @param block - if True, block until room in queue, if False may throw queue.Full exception
    def put(self, pkt, in_or_out, block=False):
        # check to see if this is an mpls packet, if so, grab the packet for the priority
        if MPLSFrame.is_byte_S_MPLS(pkt):
            p = NetworkPacket.from_byte_S(MPLSFrame.from_byte_S(pkt).pkt_S)
        else:
            # or just grab the priority
            p = NetworkPacket.from_byte_S(pkt)

        if in_or_out == 'out':
            print('putting packet in the OUT queue') #:-)
            if p.priority == 1:
                self.out_queue_1.put(pkt,block)
            elif p.priority == 0:
                self.out_queue_0.put(pkt,block)
            else:
                print('Unrecognized priority')
        else:
            if p.priority == 1:
                self.in_queue_1.put(pkt,block)
            elif p.priority == 0:
                self.in_queue_0.put(pkt,block)
            else:
                print('Unrecognized priority')

    def is_queue_empty(self, in_or_out):
        if in_or_out == 'in':
            return self.in_queue_1.empty() and self.in_queue_0.empty()
        else:
            return self.out_queue_1.empty() and self.out_queue_0.empty()

    def get_qsize(self, in_or_out):
        if in_or_out == 'in':
            return self.in_queue_1.qsize() + self.in_queue_0.qsize()
        else:
            return self.out_queue_1.qsize() + self.out_queue_0.qsize()



## Implements a network layer packet (different from the RDT packet
# from programming assignment 2).
# NOTE: This class will need to be extended to for the packet to include
# the fields necessary for the completion of this assignment.
class NetworkPacket:
    ## packet encoding lengths
    dst_addr_S_length = 5
    prot_S_length = 1
    priority_S_length = 1

    ##@param dst_addr: address of the destination host
    # @param data_S: packet payload
    # @param prot_S: upper layer protocol for the packet (data, or control)
    def __init__(self, dst_addr, prot_S, data_S, priority =0):
        self.dst_addr = dst_addr
        self.data_S = data_S
        self.prot_S = prot_S
        self.priority = priority

    ## called when printing the object
    def __str__(self):
        return self.to_byte_S()

    ## convert packet to a byte string for transmission over links
    def to_byte_S(self):
        byte_S = str(self.dst_addr).zfill(self.dst_addr_S_length)
        if self.prot_S == 'data':
            byte_S += '1'
        elif self.prot_S == 'control':
            byte_S += '2'
        else:
            raise('%s: unknown prot_S option: %s' %(self, self.prot_S))

        if self.priority > 1:
            raise('%s: unknown priority: %s' %(self, self.priority))

        byte_S += str(self.priority)
        byte_S += self.data_S
        return byte_S

    ## extract a packet object from a byte string
    # @param byte_S: byte string representation of the packet
    @classmethod
    def from_byte_S(self, byte_S):
        dst_addr = int(byte_S[0 : NetworkPacket.dst_addr_S_length])
        prot_S = byte_S[NetworkPacket.dst_addr_S_length : NetworkPacket.dst_addr_S_length + NetworkPacket.prot_S_length]
        if prot_S == '1':
            prot_S = 'data'
        elif prot_S == '2':
            prot_S = 'control'
        else:
            raise('%s: unknown prot_S field: %s' %(self, prot_S))
        priority = int(byte_S[NetworkPacket.dst_addr_S_length + NetworkPacket.prot_S_length : NetworkPacket.dst_addr_S_length + NetworkPacket.prot_S_length + NetworkPacket.priority_S_length])
        if priority > 1:
            raise('%s: unknown priority: %s' %(self, self.priority))
        data_S = byte_S[NetworkPacket.dst_addr_S_length + NetworkPacket.prot_S_length + NetworkPacket.priority_S_length: ]
        return self(dst_addr, prot_S, data_S, priority)

## Implement a MLPS network frame that encapsulates a network packet
class MPLSFrame:
    label_S_length = 20
    exp_S_length = 3
    # special_S = "バス" # Don't blink; decorate!
    special_S = "kk" # Don't blink; decorate!
    special_S_length = 2

    def __init__(self, label, exp, pkt_S):
        self.label = label
        self.exp = exp
        self.pkt_S = pkt_S

    def __str__(self):
        print(self.to_byte_S() + str(pkt))

    def to_byte_S(self):
        byte_S = MPLSFrame.special_S
        byte_S += str(self.label).zfill(self.label_S_length)
        byte_S += str(self.exp).zfill(self.exp_S_length)
        byte_S += self.pkt_S
        # print("debugging:\nbyte_S: %s\nlabel: %s\nexp: %s\npkt_S: %s\n" % (byte_S, self.label, self.exp, self.pkt_S))
        return byte_S

    @classmethod
    def from_byte_S(self, byte_S):
        label = int(byte_S[MPLSFrame.special_S_length : MPLSFrame.special_S_length + MPLSFrame.label_S_length])
        exp = int(byte_S[MPLSFrame.special_S_length + MPLSFrame.label_S_length : MPLSFrame.special_S_length + MPLSFrame.label_S_length + MPLSFrame.exp_S_length])
        pkt_S = byte_S[MPLSFrame.special_S_length + MPLSFrame.label_S_length + MPLSFrame.exp_S_length: ]
        # print("debugging:\nbyte_S: %s\nlabel: %s\nexp: %s\npkt_S: %s\n" % (byte_S, label, exp, pkt_S))
        return MPLSFrame(label, exp, pkt_S)

    @classmethod
    def is_byte_S_MPLS(self, byte_S):
        return (byte_S[0:MPLSFrame.special_S_length]) == MPLSFrame.special_S


## Implements a network host for receiving and transmitting data
class Host:

    ##@param addr: address of this node represented as an integer
    def __init__(self, addr):
        self.addr = addr
        self.intf_L = [Interface()]
        self.stop = False  #for thread termination
        self.pkt_queue_0 = []
        self.pakt_queue_1 = []

    ## called when printing the object
    def __str__(self):
        return 'Host_%s' % (self.addr)


    ## create a packet and enqueue for transmission
    # @param dst_addr: destination address for the packet
    # @param data_S: data being transmitted to the network layer
    def udt_send(self, dst_addr, data_S, priority = 0):
        p = NetworkPacket(dst_addr, 'data', data_S, priority)
        print('%s: sending packet "%s"  with priority: %s' % (self, p, priority))
        self.intf_L[0].put(p.to_byte_S(), 'out') #send packets always enqueued successfully

    ## receive packet from the network layer
    def udt_receive(self):
        pkt_S = self.intf_L[0].get('in')
        if pkt_S is not None:
            print('%s: received packet "%s"' % (self, pkt_S))

    ## thread target for the host to keep receiving data
    def run(self):
        print (threading.currentThread().getName() + ': Starting')
        while True:
            #receive data arriving to the in interface
            self.udt_receive()
            #terminate
            if(self.stop):
                print (threading.currentThread().getName() + ': Ending')
                return



## Implements a multi-interface router described in class
class Router:

    ##@param name: friendly router name for debugging
    # @param intf_cost_L: outgoing cost of interfaces (and interface number)
    # @param rt_tbl_D: routing table dictionary (starting reachability), eg. {1: {1: 1}} # packet to host 1 through interface 1 for cost 1
    # @param max_queue_size: max queue length (passed to Interface)
    def __init__(self, name, intf_cost_L, intf_capacity_L, rt_tbl_D, max_queue_size, mpls_tbl_L=None):
        self.stop = False #for thread termination
        self.name = name
        #create a list of interfaces
        #note the number of interfaces is set up by out_intf_cost_L
        assert(len(intf_cost_L) == len(intf_capacity_L))
        self.intf_L = []
        for i in range(len(intf_cost_L)):
            self.intf_L.append(Interface(intf_cost_L[i], max_queue_size, intf_capacity_L[i]))
        #set up the routing table for connected hosts
        self.rt_tbl_D = rt_tbl_D
        #set up the mpls routing table
        self.mpls_tbl_L = mpls_tbl_L

    ## called when printing the object
    def __str__(self):
        return 'Router_%s' % (self.name)

    ## look through the content of incoming interfaces and
    # process data and control packets
    def process_queues(self):
        for i in range(len(self.intf_L)):
            pkt_S = None
            #get packet from interface i
            pkt_S = self.intf_L[i].get('in')
            #if packet exists make a forwarding decision
            if pkt_S is not None:
                # check to see if we have an mpls routing table, if we do, do the mpls shit
                if not self.mpls_tbl_L == None:
                    # check if packet is mpls packet, if it isn't, make it one
                    if not MPLSFrame.is_byte_S_MPLS(pkt_S):
                        # logic on how to turn a normal packet into MPLS
                        p = NetworkPacket.from_byte_S(pkt_S)
                        for mpls_tbl in self.mpls_tbl_L:
                            if mpls_tbl['dest'] == p.dst_addr:
                                pkt_S = MPLSFrame(mpls_tbl['l_out'], p.priority, pkt_S).to_byte_S()
                                # forward the mpls packet
                                try:
                                    # put it in da queue
                                    self.intf_L[mpls_tbl['i_out']].put(pkt_S, 'out', True)
                                    return
                                except queue.Full:
                                    print('%s: MPLS frame packet "%s" lost on interface %d' % (self, m, mpls_tbl['i_out']))
                        # if we don't have the destination of the packet in our mpls table, forward the packet as usual
                        print("%s: destination address (%d) is not found in the mpls table" % (self.name, p.dst_addr))
                        self.process_normal_packet(pkt_S, i)
                    else:
                        # forward the mpls packet
                        self.forward_MPLS(pkt_S, i)
                else:
                    # since we don't have an mpls tbl, forward the packet as usual
                    self.process_normal_packet(pkt_S, i)

    ## forwarding the packet as usual
    ## @param byte_S string of the packet to forward
    def process_normal_packet(self, byte_S, i):
        p = NetworkPacket.from_byte_S(byte_S) #parse a packet out
        if p.prot_S == 'data':
            self.forward_packet(p, i)
        elif p.prot_S == 'control':
            self.update_routes(p, i)
        else:
            raise Exception('%s: Unknown packet type in packet %s' % (self, p))

    ## forward the packet according to the routing table
    #  @param p Packet to forward
    #  @param i Incoming interface number for packet p
    def forward_packet(self, p, i):
        try:
            # Forwarding table to find the appropriate outgoing interface
            if p.dst_addr not in self.rt_tbl_D:
                print("%s: destination address (%d) is not found in the routing table" % (self.name, p.dst_addr))
                return
            min_c_int = min(self.rt_tbl_D[p.dst_addr],key=self.rt_tbl_D[p.dst_addr].get)
            self.intf_L[min_c_int].put(p.to_byte_S(), 'out', True)
            print('%s: forwarding packet "%s" from interface %d to %d' % (self, p, i, min_c_int))
        except queue.Full:
            #Need to update this assuming outgoing interface is (i+1)%2
            print('%s: packet "%s" lost on interface %d' % (self, p, i))
            pass

    ## forward the mpls packet according tot he mpls routing table
    # @param m MPLS packet to forward
    def forward_MPLS(self, m, i):
        m = MPLSFrame.from_byte_S(m)
        for mpls_tbl in self.mpls_tbl_L:
            if mpls_tbl['l_in'] == m.label:
                # set our packet label to the new label based off our table
                m.label = mpls_tbl['l_out']
                # grab our interface for this label
                mi = mpls_tbl['i_out']
                try:
                    # put it in da queue
                    self.intf_L[mi].put(m.to_byte_S(), 'out', True)
                except queue.Full:
                    print('%s: MPLS frame packet "%s" lost on interface %d' % (self, m, mi))
                return
        print('%s: MPLS label address (%s) is not found in the mpls table. Decapsulating packet and send as NetworkPacket to destination.' % (self, m.label))
        self.process_normal_packet(m.pkt_S, i)



    ## forward the packet according to the routing table
    #  @param p Packet containing routing information
    #  @param i Incoming interface number for packet p
    def update_routes(self, p, i):
        print('%s: Received routing update %s from interface %d' % (self, p, i))

        p_rt_tbl = RouterPacket.from_n_pkt(p).table
        p_i_c = self.intf_L[i].cost
        flag = False

        for p_host in p_rt_tbl:
            if p_host not in self.rt_tbl_D.keys():
                self.rt_tbl_D[p_host] = {}
                self.rt_tbl_D[p_host][i]= min(p_rt_tbl[p_host], key=p_rt_tbl[p_host].get) + p_i_c
                flag = True
            elif min(p_rt_tbl[p_host], key=p_rt_tbl[p_host].get) + p_i_c < min(self.rt_tbl_D[p_host], key=self.rt_tbl_D[p_host].get):
                self.rt_tbl_D[p_host][i]= min(p_rt_tbl[p_host], key=p_rt_tbl[p_host].get) + p_i_c
                flag = True

        # Broadcast our table to our interfaces
        if flag:
            for intf in range(len(self.intf_L)):
                self.send_routes(intf)

    ## send out route update
    # @param i Interface number on which to send out a routing update
    def send_routes(self, i):
        # a sample route update packet
        p = RouterPacket(self.rt_tbl_D).to_n_pkt()
        try:
            #TODO: add logic to send out a route update
            print('%s: sending routing update "%s" from interface %d' % (self, p, i))
            self.intf_L[i].put(p.to_byte_S(), 'out', True)
        except queue.Full:
            print('%s: packet "%s" lost on interface %d' % (self, p, i))
            pass

    ## Print routing table
    def print_routes(self):
        # print the router name
        print("Router %s:" % self.name)
        # print the routes as a two dimensional table for easy inspection
        # print all the hosts
        for host in self.rt_tbl_D:
            print("\tHost %s" % host, end="")
        print()
        # for each interface print cost to hosts
        for interface in range(len(self.intf_L)):
            # print the interface name
            print("int %d" % interface, end="\t")
            # if exist, print the cost to host or ~ as unknown
            for host in self.rt_tbl_D:
                if interface in list(self.rt_tbl_D[host].keys()):
                    # print cost
                    print(self.rt_tbl_D[host][interface], end="\t")
                else:
                    print("~", end="\t")
            print()
        print("\n")

    ## thread target for the host to keep forwarding data
    def run(self):
        print (threading.currentThread().getName() + ': Starting')
        while True:
            self.process_queues()
            if self.stop:
                print (threading.currentThread().getName() + ': Ending')
                return

class RouterPacket:
    # Use the NetworkPacket to do shit, encapsulate our shit into that shit dude
    # Identify vector protcol parameters per packet and make vars
    def __init__(self, table):
        self.table = table

    def __str__(self):
        return self.from_byte_S()

    def to_byte_S(self):
        byte_S = ""
        for host in self.table:
            for interface in self.table[host]:
                byte_S += " " + str(host) + ":" + str(interface) + ":" + str(self.table[host][interface])
        return byte_S

    def to_n_pkt(self):
        return NetworkPacket(0, 'control', self.to_byte_S())

    @classmethod
    def from_byte_S(self, byte_S):
        self.table = {}
        row = byte_S[1:].split(" ")
        for buss in row:
            bus = buss.split(":")
            bus[0] = int(bus[0])
            if bus[0] not in list(self.table.keys()):
                self.table[bus[0]] = {}
            self.table[bus[0]][int(bus[1])]=int(bus[2])
        return self

    @classmethod
    def from_n_pkt(self, n_pkt):
        return self.from_byte_S(n_pkt.data_S)
