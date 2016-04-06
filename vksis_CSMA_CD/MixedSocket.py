from socket import*
import struct

class MixedSocket(socket):

    def __init__(self,family=AF_INET, type=SOCK_STREAM, proto=0, fileno=None,**kwargs):
        return super().__init__(family, type, proto, fileno, **kwargs)
      
    def join_group(self,group_addr,interf_addr=INADDR_ANY,multicast_scope=1):
        mreq = struct.pack('4sl',inet_aton(group_addr),INADDR_ANY) if interf_addr==INADDR_ANY else struct.pack('4s4s',inet_aton(group_addr),inet_aton(interf_addr)) 
        self.setsockopt(IPPROTO_IP,IP_ADD_MEMBERSHIP,mreq)
        #default                                                        
        self.setsockopt(IPPROTO_IP,IP_MULTICAST_TTL,struct.pack('b',multicast_scope))
         

    