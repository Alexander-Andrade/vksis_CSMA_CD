from socket import* 
import sys
import threading
from enum import Enum,unique
import struct
import time
from func_algorithms import*
import os
import random
import math


def interface_ip(list=False,**kwargs):
    hostname = kwargs.get('hostname',gethostname())
    proto = kwargs.get('proto',AF_INET)
    hint = kwargs.get('hint')
    addrInfoList = getaddrinfo(hostname,None,proto)
    #127.0.0.0/8 - loopback IP addresses
    ip_list = [addr_info[4][0] for addr_info in addrInfoList if not addr_info[4][0].startswith('127.')] if not hint else \
              [addr_info[4][0] for addr_info in addrInfoList if addr_info[4][0].startswith(hint)]
    if list:
        return ip_list  
    return min(ip_list) if ip_list else None


@unique
class FrameType(Enum):
    Data = 0
    GreetingRequest = 1
    GreetingReply = 2
    Leaving = 3
    Jam = 4


class Frame:

    def __init__(self,**kwargs):
        self.host_id = kwargs.get('host_id')
        self.type = kwargs.get('type',FrameType.Data)
        data = kwargs.get('data',b'')
        self.data = data if type(data) == type(bytes()) else data.encode('utf-8')
        self.frame = kwargs.get('frame',b'')
        if self.frame != b'':
            self.unpack()

    def pack(self):
        self.frame = struct.pack('!HB',self.host_id,self.type.value) + self.data
        return self.frame

    def unpack(self, frame=None):
        if frame:
            self.frame = frame
        header_size = struct.calcsize('HB')
        self.host_id,type_val = struct.unpack('!HB',self.frame[:header_size])
        self.type = FrameType(type_val)
        self.data = self.frame[header_size:]
        return(self.host_id,self.type,self.data)

    def __repr__(self):
            return 'Frame (host_id={},{},{})'.format(self.host_id,self.type, self.data.decode(encoding='utf-8'))
        
    def __str__(self):
        return self.data.decode(encoding='utf-8')

    def __bytes__(self):
        return self.frame if self.frame != b'' else self.pack()
  

class Peer:
    def __init__(addr,id):
        self.from_addr_id(addr,id)

    def to_addr(self):
        return (self.ip,self.port)

    def from_addr_id(self,addr,id):
        self.ip = addr[0]
        self.port = addr[1]
        self.id = id

    def to_bytes(self):
        return inet_aton(self.ip) + struct.pack('!HH',self.port,self.id)    
    
    def __bytes__(self):
        return self.to_bytes() 

    def from_bytes(self,byte_peer):
        self.ip = inet_ntoa(byte_peer[:4])
        self.port,self.id = struct.unpack('!HH',byte_peer[4:])

    def __repr__(self):
        return 'Peer (ip={},port={},id={})'.format(self.ip,self.port,self.id)


class Host:

    def __init__(self,group,group_port,**kwargs):
        #host id unsigned long long
        self.id = random.randrange(0, int(math.pow(2, struct.calcsize('H')*8)))
        self.group_port = int(group_port)
        self.group = group
        self.mreq = b''
        self.interf_ip = interface_ip()
        self.group_sock = socket(AF_INET,SOCK_DGRAM,IPPROTO_UDP)
        #can listen a busy port 
        self.group_sock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
        self.group_sock.bind((self.interf_ip,self.group_port)) 
        self.private_sock = socket(AF_INET,SOCK_DGRAM,IPPROTO_UDP)
        self.__join_group()
        #time of the frame transfer and to leave the medium
        self.frame_transf_interv = kwargs.get('frame_transf_interv',0.7)
        self.last_sending_timestemp = 0
        self.last_recv_timestemp = 0
        self.inter_frame_gap = kwargs.get('inter_frame_gap',0.5)
        self.min_frame_gap = kwargs.get('min_frame_gap',self.frame_transf_interv)
        self.max_frame_gap = kwargs.get('max_frame_gap',6.0)
        self.max_sending_attempts = 16
        self.peers = []
        self.max_greeting_reply_time = 3
        self.actions = {FrameType.Data : self.handle_data,
                        FrameType.GreetingRequest : self.handle_greeting_reguest,
                        FrameType.GreetingReply : self.handle_greeting_reply,
                        FrameType.Leaving : self.handle_leaving,
                        FrameType.Jam : self.handle_jam}
        self.on_jam_come_event = threading.Event()
        self.on_jam_come_event.set()  
        self.frame_sending_thread = threading.Thread(target=self.frame_sending_routine,args=(self.on_jam_come_event,))


    def __join_group(self):
        self.mreq = struct.pack('4s4s',inet_aton(self.group),inet_aton(self.interf_ip))
        self.group_sock.setsockopt(IPPROTO_IP,IP_ADD_MEMBERSHIP,self.mreq)
        #default
        self.group_sock.setsockopt(IPPROTO_IP,IP_MULTICAST_TTL,struct.pack('b',1))

    def __unjoin_group(self):
        self.group_sock.setsockopt(SOL_IP,IP_DROP_MEMBERSHIP,self.mreq)

    def group_send(self,msg):
        self.private_sock.sendto(msg,(self.group,self.group_port))

    def send(self,msg,addr):
        self.private_sock.sendto(msg,addr)

    def recv(self,num):
        return self.group_sock.recvfrom(num)

    def handle_data(self,peer_ident,frame):
        #skip data
        pass
    
    def reg_unknown_peer(self,peer_ident):
        if peer_ident not in self.peers:
            self.peers.append(peer_ident)

    @staticmethod
    def list_to_bytes(list,type_symb):
        pass

    @staticmethod
    def bytes_to_list(list,type_symb):
        pass

    def handle_greeting_reguest(self,peer_ident,frame):
        self.reg_unknown_peer(peer_ident)
        #send self peer-list as greeting reply
        #set timeout and listen bus, if enother peer managed first
        reply_after_t = random.uniform(0, self.max_greeting_reply_time)   
        #listen bus with timeout
        self.group_sock.settimeout(reply_after_t)
        try:
            self.group_sock.recvfrom(1024)
        except OSError as e:
            #this host is first-> send peers-list
            #self.
            pass

    def handle_greeting_reply(self,peer_ident,frame):
        pass


    def handle_leaving(self,peer_,frame):
        if peer in self.peers:
            self.peers.remove(peer)

    def handle_jam(self,peer,frame):
        #stop sending frames while is collision on the media(bus)
        self.on_jam_come_event.clear()
        time.sleep(self.frame_transf_interv)
        #resume sending thread
        self.on_jam_come_event.set()
        
    def is_thishost_sender(self,peer):
        return peer.ip == self.interf_ip and peer.port == self.private_sock.getsockname()[1] and self.id==peer.id
         
    def is_medium_busy(self):
        return self.frame_transf_interv > time.time() - self.last_sending_timestemp

    def is_collision(self):
        return self.frame_transf_interv > time.time() - self.last_recv_timestemp

    def calc_exp_delay(self,n_transf_attempts):
        k = min(n_transf_attempts,10)
        r = random.randrange(0,math.pow(2,k))
        return r * self.frame_transf_interv

    def send_frame(self):
        n_transf_attempts = 0
        while True:
            #checking if medium(bus) is busy (pooling)
            if self.is_medium_busy():
                continue
            #waiting for Inter Frame Gap elapced
            time.sleep(self.inter_frame_gap)
            #begin transfer  and select randomly any peer to send frame
            peer_ident = random.choice(self.peers)
            self.send(bytes(Frame(host_id=self.id,data='data')),peer_ident.to_addr())
            #catch sending time stemp
            self.last_sending_timestemp = time.time()
            #checking collisions
            #collision is when time from the last received frame not elapsed
            if self.is_collision():
                print('collision detected')
                #sending jam-signal
                self.group_send(bytes(Frame(host_id=self.id,type=FrameType.Jam)))
                n_transf_attempts += 1
                if n_transf_attempts > self.max_sending_attempts:
                    #fail to send frame
                    print('fail to send frame')
                #calculate exponential delay 
                exp_delay = self.calc_exp_delay(n_transf_attempts)
                #and wait this delay
                time.sleep(exp_delay)


    def delay_to_prepare_frame(self):
        #randomize sending activity
        nextframe_t = random.uniform(self.min_frame_gap, self.max_frame_gap)
        #waiting when next frame will be ready to transfer
        time.sleep(nextframe_t)

    def frame_sending_routine(self,on_jam_come_event):
        while True:
            self.delay_to_prepare_frame()
            #stop sending frames when jam sygnal arrived
            on_jam_come_event.wait()
            if self.peers: 
                self.send_frame()
            
    def listen_bus(self):
        #sender_add = sender_ip + sender_port
        recv_frame,sender_addr=self.recv(1024)
        frame = Frame(frame=recv_frame)
        #peer = sender_ip + sender_port + sender_id (sender_id is necessary for abylity to hang several processes to the port)
        peer = Peer(sender_addr,frame.host_id)
        return (frame,peer)

    def group_listening_and_replies(self):
        while True:
            frame,peer=self.listen_bus()
            #test if frame is from this host
            if self.is_thishost_sender(peer):
                continue
            #mark that the foreign frame arrived
            self.last_recv_timestemp = time.time()
            print(repr(frame))
            self.actions[frame.type](peer,frame)


    def run(self):
        #notify all devices on the bus
        self.group_send(bytes(Frame(host_id=self.id,type=FrameType.GreetingRequest)))
        #start sending some data to the peers
        self.frame_sending_thread.start()
        #listen bus and act accordinatly
        self.group_listening_and_replies()


if __name__ == '__main__':
     li = [100,1,3]
     bli = bytearray(li)
     print(bli)
     print(list(bli))
     #random.seed()
     #host = Host(sys.argv[1],sys.argv[2])
     #host.run()