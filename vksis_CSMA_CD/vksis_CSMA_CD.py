from socket import* 
import sys
from threading import Thread
from enum import Enum,unique
import struct
import time
from func_algorithms import*
import os
import random
import math


def interface_ip(list=False,**kwargs):
    hostname = kwargs.get('hostname',gethostname())
    proto = kwargs.get('proto',AF_INET)
    hint = kwargs.get('hint')
    addrInfoList = getaddrinfo(hostname,None,proto)
    #127.0.0.0/8 - loopback IP addresses
    ip_list = [addr_info[4][0] for addr_info in addrInfoList if not addr_info[4][0].startswith('127.')] if not hint else \
              [addr_info[4][0] for addr_info in addrInfoList if addr_info[4][0].startswith(hint)]
    if list:
        return ip_list  
    return min(ip_list) if ip_list else None


@unique
class FrameType(Enum):
    Data = 0
    Greeting = 1
    Leaving = 2
    Jam = 3


class Frame:

    def __init__(self,**kwargs):
        self.host_id = kwargs.get('host_id')
        self.type = kwargs.get('type',FrameType.Data)
        data = kwargs.get('data',b'')
        self.data = data if type(data) == type(bytes()) else data.encode('utf-8')
        self.frame = kwargs.get('frame',b'')
        if self.frame != b'':
            self.unpack()

    def pack(self):
        self.frame = struct.pack('!HB',self.host_id,self.type.value) + self.data
        return self.frame

    def unpack(self, frame=None):
        if frame:
            self.frame = frame
        header_size = struct.calcsize('HB')
        self.host_id,type_val = struct.unpack('!HB',self.frame[:header_size])
        self.type = FrameType(type_val)
        self.data = self.frame[header_size:]
        return(self.host_id,self.type,self.data)

    def __repr__(self):
            return 'Frame (host_id={},{},{})'.format(self.host_id,self.type, self.data.decode(encoding='utf-8'))
        
    def __str__(self):
        return self.data.decode(encoding='utf-8')

    def __bytes__(self):
        return self.frame if self.frame != b'' else self.pack()
  

class Host:

    def __init__(self,group,group_port,**kwargs):
        #host id unsigned long long
        self.id = random.randrange(0, int(math.pow(2, struct.calcsize('H')*8)))
        self.group_port = int(group_port)
        self.group = group
        self.mreq = b''
        self.interf_ip = interface_ip()
        self.group_sock = socket(AF_INET,SOCK_DGRAM,IPPROTO_UDP)
        self.group_sock.bind((self.interf_ip,self.group_port)) 
        self.send_sock = socket(AF_INET,SOCK_DGRAM,IPPROTO_UDP)
        self.__join_group()
        #time to send the frame and to leave the medium
        self.frame_transf_interv = kwargs.get('frame_transf_interv',0.7)
        self.frame_recv_interv
        self.last_sending_timestemp = 0
        self.last_recv_timestemp = 0
        self.inter_frame_gap = kwargs.get('inter_frame_gap',0.5)
        self.min_frame_gap = kwargs.get('min_frame_gap',self.frame_transf_interv)
        self.max_frame_gap = kwargs.get('max_frame_gap',6.0)
        self.n_sending_attempts = 16
        self.peers = set()
        self.actions = {FrameType.Data : self.handle_data,
                        FrameType.Greeting : self.handle_greeting,
                        FrameType.Leaving : self.handle_leaving,
                        FrameType.Jam : self.handle_jam}
        self.frame_sending_thread = Thread(target=self.frame_sending_routine,args=())


    def __join_group(self):
        #mreq = struct.pack('4sl',inet_aton(self.group),INADDR_ANY)
        self.mreq = struct.pack('4s4s',inet_aton(self.group),inet_aton(self.interf_ip))
        self.group_sock.setsockopt(IPPROTO_IP,IP_ADD_MEMBERSHIP,self.mreq)
        #can listen a busy port 
        self.group_sock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
        #default
        self.group_sock.setsockopt(IPPROTO_IP,IP_MULTICAST_TTL,struct.pack('b',1))

    def __unjoin_group(self):
        self.group_sock.setsockopt(SOL_IP,IP_DROP_MEMBERSHIP,self.mreq)

    def group_send(self,msg):
        self.send_sock.sendto(msg,(self.group,self.group_port))

    def send(self,msg,addr):
        self.send_sock.sendto(msg,addr)

    def recv(self,num):
        return self.group_sock.recvfrom(num)

    def handle_data(self,peer_addr,frame):
        print('data action')
    
    def handle_greeting(self,peer_addr,frame):
        print('greeting action')

    def handle_leaving(self,peer_addr,frame):
        print('leaving action')

    def handle_jam(self,peer_addr,frame):
        print('jam action')
        
    def is_thishost_sender(self,sender_ident):
        return sender_ident[0] == self.interf_ip and sender_ident[1] == self.send_sock.getsockname()[1] and self.id==sender_ident[2]
         
    def is_medium_busy(self):
        return self.frame_transf_interv > time.time() - self.last_sending_timestemp

    def frame_sending_routine(self):
        nextframe_t = 0
        #notify all devices on the bus
        self.group_send(bytes(Frame(host_id=self.id,type=FrameType.Greeting)))
        while True:
            #randomize sending activity
            nextframe_t = random.uniform(self.min_frame_gap, self.max_frame_gap)
            #waiting when next frame will be ready to transfer
            time.sleep(nextframe_t)
            #checking if medium(bus) is busy (pooling)
            if self.is_medium_busy():
                continue
            #waiting for Inter Frame Gap elapced
            time.sleep(self.inter_frame_gap)
            #begin transfer
            self.group_send(bytes(Frame(host_id=self.id,data='data')))
            #catch sending time stemp
            self.last_sending_timestemp = time.time()
            #checking collisions
            #collision is when time from the last received frame not elapsed


    def run(self):
        self.frame_sending_thread.start()
        while True:
            #sender_add = sender_ip + sender_port
            recv_frame,sender_addr=self.recv(1024)
            frame = Frame(frame=recv_frame)
            #sender_ident = sender_ip + sender_port + sender_id (sender_id is necessary for abylity to hang several processes to the port)
            sender_ident = (sender_addr[0],sender_addr[1],frame.host_id)
            #test if frame is from this host
            if self.is_thishost_sender(sender_ident):
                continue
            #mark that the foreign frame arrived
            self.last_recv_timestemp = time.time()
             
            print(repr(frame))
            self.actions[frame.type](sender_ident,frame)


if __name__ == '__main__':
     random.seed()
     host = Host(sys.argv[1],sys.argv[2])
     host.run()