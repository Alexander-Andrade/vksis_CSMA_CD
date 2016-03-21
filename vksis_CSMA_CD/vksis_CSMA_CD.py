from socket import* 
import sys
from threading import Thread
from enum import Enum,unique
import struct
import time
from func_algorithms import*

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


class Packet:

    def __init__(self,**kwargs):
        self.frame_type = kwargs.get('frame_type',FrameType.Data)
        self.packet = kwargs.get('packet',b'')
        self.data = kwargs.get('data',b'')

    def pack(self):
        self.packet = struct.pack('!B',self.frame_type.value) + self.data
        return self.packet

    def unpack(self, packet=None):
        if packet:
            self.packet = packet
        self.frame_type = struct.unpack('!B',self.packet[:1])[0]
        self.data = self.packet[1:]
        return(self.frame_type,self.data)

  

class Host:

    def __init__(self,group,port,**kwargs):
        self.port = int(port)
        self.group = group
        self.mreq = b''
        self.net_interf = interface()
        self.group_sock = socket(AF_INET,SOCK_DGRAM,IPPROTO_UDP)
        self.group_sock.bind((self.net_interface,port)) 
        self.send_sock = socket(AF_INET,SOCK_DGRAM,IPPROTO_UDP)
        self.__join_group()
        self.send_period = kwargs.get('send_timeout',2)

    def __join_group(self):
        #mreq = struct.pack('4sl',inet_aton(self.group),INADDR_ANY)
        self.mreq = struct.pack('4s4s',inet_aton(self.group),inet_aton(self.net_interf))
        self.group_sock.setsockopt(IPPROTO_IP,IP_ADD_MEMBERSHIP,self.mreq)
        self.group_sock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
        #default
        self.group_sock.setsockopt(IPPROTO_IP,IP_MULTICAST_TTL,struct.pack('b',1))

    def __unjoin_group(self):
        self.group_sock.setsockopt(SOL_IP,IP_DROP_MEMBERSHIP,self.mreq)

    def group_send(self,sock,msg):
        self.sock.sendto(msg,(self.group,self.port))

    def send(self,msg,addr):
        self.send_sock.sendto(msg,addr)

    def recv(self,num):
        return self.group_sock.recvfrom(num)

if __name__ == '__main__':
     host = Host(sys.argv[1],sys.argv[2])
