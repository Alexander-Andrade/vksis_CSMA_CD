import sys
import pickle
import random
from Host import Host
from socket import*
from MixedSocket import MixedSocket
from net_interface import*
import time
from Frame import Frame
from FrameType import FrameType

if __name__ == '__main__':
     #test
     '''
     sock = MixedSocket(AF_INET,SOCK_DGRAM,IPPROTO_UDP)

     ms = MixedSocket(AF_INET,SOCK_DGRAM,IPPROTO_UDP)
     ms.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
     ms.bind(('192.168.1.2',6000))
     ms.join_group('224.0.0.1','192.168.1.2')

     ms1 = MixedSocket(AF_INET,SOCK_DGRAM,IPPROTO_UDP)
     ms1.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
     ms1.bind(('192.168.1.2',6000))
     ms1.join_group('224.0.0.1','192.168.1.2')
    
     sock.send_frame_to(Frame(host_id=4,type=FrameType.GreetingReply,data='some str'),('224.0.0.1',6000))
     print(ms1.recv_frame_from()) 
     print(ms.recv_frame_from())
     '''
     random.seed()
     host = Host(sys.argv[1],sys.argv[2])
     host.run()