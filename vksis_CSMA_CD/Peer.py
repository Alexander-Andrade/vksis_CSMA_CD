class Peer:
    def __init__(self,interf,id):
        self.interf = interf
        self.id = id

    def to_addr(self):
        return (self.interf, self.id)

    def __repr__(self):
        return 'Peer (ip={}, id={})'.format(self.ip, self.id)