from socket import* 
import sys
from threading import Thread
from enum import Enum,unique
import struct
import time
from func_algorithms import*
import os
import random


def interface(list=False,**kwargs):
    hostname = kwargs.get('hostname',gethostname())
    proto = kwargs.get('proto',AF_INET)
    hint = kwargs.get('hint')
    addrInfoList = getaddrinfo(hostname,None,proto)
    #127.0.0.0/8 - loopback IP addresses
    interfs = [addr_info[4][0] for addr_info in addrInfoList if not addr_info[4][0].startswith('127.')] if not hint else \
              [addr_info[4][0] for addr_info in addrInfoList if addr_info[4][0].startswith(hint)]
    if list:
        return interfs  
    return min(interfs) if interfs else None


@unique
class FrameType(Enum):
    Data = 0
    Greeting = 1
    Leaving = 2
    Jam = 3


class Frame:

    def __init__(self,**kwargs):
        self.type = kwargs.get('frame_type',FrameType.Data)
        data = kwargs.get('data',b'')
        self.data = data if type(data) == type(bytes()) else data.encode('utf-8')
        self.frame = kwargs.get('frame',b'')
        if self.frame != b'':
            self.unpack()

    def pack(self):
        self.frame = struct.pack('!B',self.type.value) + self.data
        return self.frame

    def unpack(self, frame=None):
        if frame:
            self.frame = frame
        self.type = FrameType( struct.unpack('!B',self.frame[:1])[0] )
        self.data = self.frame[1:]
        return(self.type,self.data)

    def __repr__(self):
            return 'Frame ({},{})'.format(self.type, self.data.decode(encoding='utf-8'))
        
    def __str__(self):
        return self.data.decode(encoding='utf-8')

    def __bytes__(self):
        return self.frame if self.frame != b'' else self.pack()
  

class Host:

    def __init__(self,group,port,**kwargs):
        self.port = int(port)
        self.group = group
        self.mreq = b''
        self.net_interf = interface()
        self.group_sock = socket(AF_INET,SOCK_DGRAM,IPPROTO_UDP)
        self.group_sock.bind((self.net_interf,self.port)) 
        self.send_sock = socket(AF_INET,SOCK_DGRAM,IPPROTO_UDP)
        self.__join_group()
        self.send_period = kwargs.get('send_period',2)
        self.minsend_freq = 1
        self.maxsend_freq = 20
        self.sending_thread = Thread(target=self.sending_routine,args=())

    def __join_group(self):
        #mreq = struct.pack('4sl',inet_aton(self.group),INADDR_ANY)
        self.mreq = struct.pack('4s4s',inet_aton(self.group),inet_aton(self.net_interf))
        self.group_sock.setsockopt(IPPROTO_IP,IP_ADD_MEMBERSHIP,self.mreq)
        self.group_sock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
        #default
        self.group_sock.setsockopt(IPPROTO_IP,IP_MULTICAST_TTL,struct.pack('b',1))

    def __unjoin_group(self):
        self.group_sock.setsockopt(SOL_IP,IP_DROP_MEMBERSHIP,self.mreq)

    def group_send(self,msg):
        self.send_sock.sendto(msg,(self.group,self.port))

    def send(self,msg,addr):
        self.send_sock.sendto(msg,addr)

    def recv(self,num):
        return self.group_sock.recvfrom(num)

    def sending_routine(self):
        nextframe_t = 0
        self.group_send(bytes(Frame(type=FrameType.Greeting)))
        #while True:
        nextframe_t = random.uniform(self.minsend_freq,self.maxsend_freq)
        self.group_send(bytes(Frame(data='data')))


    def run(self):
        self.sending_thread.start()
        while True:
            recv_frame,addr=self.recv(1024)
            print(repr(Frame(frame=recv_frame)))



if __name__ == '__main__':
     host = Host(sys.argv[1],sys.argv[2])
     host.run()