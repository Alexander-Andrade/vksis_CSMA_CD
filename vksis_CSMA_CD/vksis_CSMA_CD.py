import sys
import pickle
import random
from Host import Host
from socket import*
from MixedSocket import MixedSocket
from net_interface import*

class cl(Host):

    def __init__(self, group, group_port, **kwargs):
        return super().__init__(group, group_port, **kwargs)


if __name__ == '__main__':
     ms = MixedSocket(AF_INET,SOCK_DGRAM,IPPROTO_UDP)
     ms.bind((interface_ip(),6000))
     ms.join_group('224.0.0.1','224.0.0.1')

     print(ms.getsockname())

     ms.sendto(b'qwerty',('224.0.0.1',6000))
     print(ms.recvfrom(1024))
     #p_list = [Peer(('172.168.1.2',6000),45020),Peer(('172.162.45.2',2300),2340),]
     #ser_pl = pickle.dumps(p_list)
     #print(pickle.loads(ser_pl))
     #random.seed()
     #host = Host(sys.argv[1],sys.argv[2])
     #host.run()