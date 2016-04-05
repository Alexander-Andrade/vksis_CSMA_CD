import struct
from FrameType import*


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