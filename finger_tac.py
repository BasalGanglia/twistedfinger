# Read username, output from non-empty factory, drop connections
# Use deferreds, to minimi...

from twisted.application import service, strports
from twisted.internet import protocol, reactor, defer
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
        return defer.succeed(self.users.get(user, b"No Such user"))

application = service.Application('finger', uid=1, gid=1)
factory = FingerFactory({b'moshez' : b'happy and well'})
strports.service("tcp:79", factory, reactor=reactor).setServiceParent(
    service.IServiceCollection(application)
)
    
    
    