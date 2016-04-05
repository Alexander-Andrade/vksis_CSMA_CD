from socket import*

class MixedSocket(socket):

    def __init__(self,family=AF_INET, type=SOCK_STREAM, proto=0, fileno=None,**kwargs):
        return super().__init__(family, type, proto, fileno, **kwargs)
      
    def join_group(self,group_addr,interf_addr=INADDR_ANY):
        net_interf = htonl(INADDR_ANY) if interf_addr==INADDR_ANY else inet_aton(self.interf_ip)   
        mreq = struct.pack('4s4s',inet_aton(self.group),net_interf)
        self.setsockopt(IPPROTO_IP,IP_ADD_MEMBERSHIP,self.mreq)
        #default 
        self.setsockopt(IPPROTO_IP,IP_MULTICAST_TTL,struct.pack('b',1))
         

    