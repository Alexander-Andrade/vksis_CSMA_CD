from socket import*
import struct
import pickle

class MixedSocket(socket):

    def __init__(self,family=AF_INET, type=SOCK_STREAM, proto=0, fileno=None,**kwargs):
        return super().__init__(family, type, proto, fileno, **kwargs)
      
    def join_group(self,group_addr,interf_addr,multicast_scope=1):
        #self.mreq = struct.pack('4sl',inet_aton(group_addr),INADDR_ANY) if interf_addr==INADDR_ANY else struct.pack('4s4s',inet_aton(group_addr),inet_aton(interf_addr)) 
        self.mreq = struct.pack('4s4s',inet_aton(group_addr),inet_aton(interf_addr))
        self.setsockopt(IPPROTO_IP,IP_ADD_MEMBERSHIP,self.mreq)
        #default                                                        
        self.setsockopt(IPPROTO_IP,IP_MULTICAST_TTL,struct.pack('b',multicast_scope))

    def leave_group(self):
        self.group_sock.setsockopt(SOL_IP,IP_DROP_MEMBERSHIP,self.mreq)

    def recvfrom_with_discarding(self,sender_addr,len):
        while True:
           data,addr = sock.recvfrom(len)
           if addr == sender_addr:
               return data

    def obj_sendto(self,obj,addr):
        serialized_obj = pickle.dumps(obj)
        ser_obj_size = len(serialized_obj)
        self.sendto(struct.pack('!H',ser_obj_size),addr)
        self.sendto(serialized_obj)

    def obj_recvfrom(self):
        obj_len,addr = self.recvfrom(1024)
        #prevent the possibility of not reading enother udp-message
        serialized_obj=self.recvfrom_with_discarding(addr,obj_len)
        return pickle.loads(serialized_obj) 

         

    