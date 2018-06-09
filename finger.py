from twisted.internet import protocol, reactor, defer, endpoints
from twisted.protocols import basic

class FingerProtocol(basic.LineReceiver):
    def lineReceived(self, user):        
        self.transport.write(self.factory.getUser(user) + b"\r\n")
        print("we received from user: {}", user)
        self.transport.loseConnection()
        
  #  def connectionMade(self):
   #     self.transport.loseConnection()

class FingerFactory(protocol.ServerFactory):
    protocol = FingerProtocol
    
    def __init__(self, users):
        self.users = users
        
    def getUser(self, user):
        return self.users.get(user, b"no such user")
    
fingerEndpoint = endpoints.serverFromString(reactor, "tcp:1079")
fingerEndpoint.listen(FingerFactory({b'moshez' : b'happy and well'}))
print("where is this even printing...")
reactor.run()
