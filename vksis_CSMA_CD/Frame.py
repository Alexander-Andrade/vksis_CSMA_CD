import struct
from FrameType import*
import pickle

class Frame:

    def __init__(self,**kwargs):
        self.host_id = kwargs.get('host_id')
        self.type = kwargs.get('type',FrameType.Data)
        self.data = kwargs.get('data',b'')
        self.frame = kwargs.get('frame',b'')
        if self.frame != b'':
            self.unpack()

    def pack(self):
        data = self.data if type(self.data) is bytes else pickle.dumps(self.data)
        self.frame = struct.pack('!HB',self.host_id,self.type.value) + data
        return self.frame

    def unpack(self, frame=None):
        if frame:
            self.frame = frame
        header_size = struct.calcsize('HB')
        self.host_id,type_val = struct.unpack('!HB',self.frame[:header_size])
        self.type = FrameType(type_val)
        bytes_data = self.frame[header_size:]
        if len(bytes_data):
            self.data = pickle.loads(bytes_data)
        return(self.host_id,self.type,self.data)

    def __repr__(self):
            return 'Frame (host_id={},type={},data={})'.format(self.host_id,self.type, self.data)
        
    def __bytes__(self):
        return self.frame if self.frame != b'' else self.pack()