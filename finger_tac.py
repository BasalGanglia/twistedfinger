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

class FingerSetterProtocol(basic.LineReceiver):
    def connectionMade(self):
        self.lines = []
    
    def lineReceived(self, line):
        self.lines.append(line)
        
    def connectionLost(self, reason):
        user = self.lines[0]
        status = self.lines[1]
        self.factory.setUser(user, status)    
    
class FingerFactory(protocol.ServerFactory):
    protocol = FingerProtocol
    
    def __init__(self, users):
        self.users = users
        
    def getUser(self, user):
        return defer.succeed(self.users.get(user, b"No Such user"))

class FingerService(service.Service):
    def __init__(self, users):
        self.users = users
        
    def getUser(self, user):
        return defer.succeed(self.users.get(user, b"no such user"))
    
    def setUser(self, user, status):
        self.users[user] = status
        
    def getFingerFactory(self):
        f = protocol.ServerFactory()
        f.protocol = FingerProtocol
        f.getUser = self.getUser
        return f
    
    def getFingerSetterFactory(self):
        
        f = protocol.ServerFactory()
        f.protocol = FingerSetterProtocol
        f.setUser = self.setUser
        return f
    
    
application = service.Application('finger', uid=1, gid=1)
f = FingerService({b'moshez' : b'happy and well'})
serviceCollection = service.IServiceCollection(application)
strports.service("tcp:79", f.getFingerFactory()
                 ).setServiceParent(serviceCollection)
strports.service("tcp:1079", f.getFingerSetterFactory()
                 ).setServiceParent(serviceCollection)
    
        
        
        

        
class FingerSetterFactory(protocol.ServerFactory):
    protocol = FingerSetterProtocol
    
    def __init__(self, FingerFactory):
        self.fingerFactory = FingerFactory
    
    def setUser(self, user, status):
        self.fingerFactory.users[user] = status
        

ff = FingerFactory({b'moshez': b'happy and well'})
fsf = FingerSetterFactory(ff)

application = service.Application('finger', uid=1, gid=1)
serviceCollection = service.IServiceCollection(application)
strports.service("tcp:79", ff).setServiceParent(serviceCollection)
strports.service("tcp:1079", fsf).setServiceParent(serviceCollection)
    
    