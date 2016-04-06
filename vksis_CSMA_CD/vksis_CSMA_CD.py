import sys
import pickle
import random
from Host import Host
from socket import*
from MixedSocket import MixedSocket
from net_interface import*

if __name__ == '__main__':
     random.seed()
     host = Host(sys.argv[1],sys.argv[2])
     host.run()