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
from Peer import Peer

if __name__ == '__main__':
     '''#test
     ms = MixedSocket(AF_INET,SOCK_DGRAM,IPPROTO_UDP)
     ms.bind(('192.168.1.2',6000))
     ms.join_group('224.0.0.1','192.168.1.2')
     print(ms.get_recv_bufsize())
     ms.send_frame_to(Frame(host_id=4,type=FrameType.GreetingReply,data=b'some str'),('224.0.0.1',6000))
     print(ms.recv_frame_from()) 
     '''
     random.seed()
     host = Host(sys.argv[1],sys.argv[2])
     host.run()