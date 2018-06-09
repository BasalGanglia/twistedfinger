from twisted.internet import protocol, reactor, defer, endpoints
from twisted.protocols import basic

class FingerProtocol(basic.LineReceiver):
    def lineReceived(self, user):        
        d = self.factory.getUser(user)
        
        def onError(err):
            return 'internal error in server'
        d.addErrback(onError)
        
        def writeResponse(message):
            self.transport.write(message + b'\r\n')
            self.transport.loseConnection()
            
        d.addCallback(writeResponse)
            

class FingerFactory(protocol.ServerFactory):
    protocol = FingerProtocol
    
    def __init__(self, users):
        self.users = users
        
    def getUser(self, user):
        return defer.succeed(self.users.get(user, b"No such user"))
    
fingerEndpoint = endpoints.serverFromString(reactor, "tcp:1079")
fingerEndpoint.listen(FingerFactory({b'moshez' : b'happy and well'}))
print("where is this even printing...")
reactor.run()
