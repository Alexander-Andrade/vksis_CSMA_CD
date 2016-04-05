import sys
import pickle
import random
from Host import Host
from socket import*

class cl(Host):

    def __init__(self, group, group_port, **kwargs):
        return super().__init__(group, group_port, **kwargs)


if __name__ == '__main__':
     p_list = [Peer(('172.168.1.2',6000),45020),Peer(('172.162.45.2',2300),2340),]
     ser_pl = pickle.dumps(p_list)
     print(pickle.loads(ser_pl))
     print(len(ser_pl))
     print((32+16+16)*3)
     #random.seed()
     #host = Host(sys.argv[1],sys.argv[2])
     #host.run()