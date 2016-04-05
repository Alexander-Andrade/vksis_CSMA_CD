
class Peer:
    def __init__(self,addr,id):
        self.from_addr_id(addr,id)

    def to_addr(self):
        return (self.ip,self.port)

    def from_addr_id(self,addr,id):
        self.ip = addr[0]
        self.port = addr[1]
        self.id = id

    def __repr__(self):
        return 'Peer (ip={},port={},id={})'.format(self.ip,self.port,self.id)