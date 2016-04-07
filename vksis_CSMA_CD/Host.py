import threading
import struct
import time
import random
import math
from socket import*
from FrameType import FrameType
from net_interface import*
from Peer import Peer
from MixedSocket import MixedSocket
from Frame import Frame
                                            
def random_unum(str_num_type,min=0):
    return random.randrange(min, int(math.pow(2, struct.calcsize(str_num_type)*8)))

class Host:

    def __init__(self,group,group_port,**kwargs):
        #host id unsigned long long
        self.id = random_unum('H')
        self.group_port = int(group_port)
        self.group = group
        self.interf_ip = interface_ip()
        self.group_sock = MixedSocket(AF_INET,SOCK_DGRAM,IPPROTO_UDP)
        #can listen a busy port 
        self.group_sock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
        self.group_sock.bind((self.interf_ip,self.group_port))
        self.group_sock.join_group(self.group, self.interf_ip)
        self.private_sock = MixedSocket(AF_INET,SOCK_DGRAM,IPPROTO_UDP)
        self.private_sock.bind((self.interf_ip,self.private_port))
        #time of the frame transfer and to leave the medium
        self.frame_transf_interv = kwargs.get('frame_transf_interv',0.7)
        self.last_sending_timestemp = 0
        self.last_recv_timestemp = 0
        self.inter_frame_gap = kwargs.get('inter_frame_gap',0.5)
        self.min_frame_gap = kwargs.get('min_frame_gap',self.frame_transf_interv)
        self.max_frame_gap = kwargs.get('max_frame_gap',6.0)
        self.max_sending_attempts = 16
        self.host_as_peer = Peer(self.interf_ip, self.id)
        self.peers = []
        self.max_greeting_reply_time = 3
        self.actions = {FrameType.Data : self.handle_data,
                        FrameType.GreetingRequest : self.handle_greeting_reguest,
                        FrameType.GreetingReply : self.handle_greeting_reply,
                        FrameType.Leaving : self.handle_leaving,
                        FrameType.Jam : self.handle_jam}
        self.stop_sending_thread_event = threading.Event()  
        self.frame_sending_thread = threading.Thread(target=self.frame_sending_routine,args=(self.stop_sending_thread_event,))

    def group_send(self,msg):
        self.private_sock.sendto(msg,(self.group,self.group_port))

    def handle_data(self,peer,frame):
        #skip data
        pass

    def reg_unknown_peer(self,peer):
        if peer not in self.peers:
            self.peers.append(peer)
    
    def stop_sending_thread(self):
        self.stop_sending_thread_event.clear()

    def resume_sending_thread(self):
        self.stop_sending_thread_event.set()

    def handle_greeting_reguest(self,peer,frame):
        #stop sending data, it overflows udp receive buffer
        self.stop_sending_thread()
        self.reg_unknown_peer(peer)
        #send self peer-list as greeting reply
        #set timeout and listen bus, if enother peer managed first
        reply_after_delay = random.uniform(0, self.max_greeting_reply_time)   
        #listen bus with timeout
        self.group_sock.settimeout(reply_after_delay)
        try:
            self.group_sock.recv_frame_from(type=FrameType.GreetingReply)
        except OSError as e:
            #this host is first-> send peers-list to the private peer socket (frame.data contains private peer socket)
            self.group_sock.send_frame_to(Frame(dst_addr=peer, type=FrameType.GreetingReply, data=self.peers+[self.host_as_peer]),(self.group,self.group_port))
        finally:
            self.group_sock.settimeout(None)
        self.resume_sending_thread()

    def handle_greeting_reply(self,peer,frame):
        #get peers-list from other peer 
        self.peers.extend(self.group_sock.recv_frame_from(type=FrameType.GreetingReply) )


    def handle_leaving(self,peer,frame):
        if peer in self.peers:
            self.peers.remove(peer)

    def handle_jam(self,peer,frame):
        #stop sending frames while is collision on the media(bus)
        print('jam')
        self.stop_sending_thread()
        time.sleep(self.frame_transf_interv)
        #resume sending thread
        self.resume_sending_thread()
             
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
            chosen_peer = random.choice(self.peers)
            self.private_sock.send_frame_to(Frame(src_addr=self.host_as_peer, dst_addr=chosen_peer, data='data'), (self.group, self.group_port))
            #catch sending time stemp
            self.last_sending_timestemp = time.time()
            #checking collisions
            #collision is when time from the last received frame not elapsed
            if self.is_collision():
                print('collision detected')
                #sending jam-signal
                self.group_sock.send_frame_to(Frame(src_addr=self.host_as_peer,type=FrameType.Jam), (self.group, self.group_port))
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

    def frame_sending_routine(self,stop_sending_thread_event):
        while True:
            self.delay_to_prepare_frame()
            #stop sending frames when jam sygnal arrived and while greeting longs
            stop_sending_thread_event.wait()
            if self.peers: 
                self.send_frame()
            
    def am_i_recepient(self, frame):
        #if there is no target address in frame
        #see source address, if it = this host -> this packet ton for tis host
        if frame.dst_addr == NOT_ADDRESSED and frame.src_addr == self.host_as_peer:
            return False
        #directed transfer
        elif frame.dst_addr == self.host_as_peer:
            return True
        #like a multicast
        else:
            return True

    def group_listening_and_replies(self):
        while True:
            frame = self.group_sock.recv_frame_from()
            #test if frame is from this host
            if not self.am_i_recepient(frame):
                continue
            #mark that the foreign frame arrived
            self.last_recv_timestemp = time.time()
            print(repr(frame))
            self.actions[frame.type](peer,frame)


    def run(self):
        #notify all devices on the bus
        self.group_sock.send_frame_to(Frame(src_addr=self.host_as_peer, type=FrameType.GreetingRequest), (self.group, self.group_port))
        #start sending some data to the peers
        self.frame_sending_thread.start()
        #listen bus and act accordinatly
        self.group_listening_and_replies()