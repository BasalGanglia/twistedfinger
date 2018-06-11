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
    def __init__(self, filename):
        self.users = {}
        self.filename = filename
        
    def _read(self):
        with open(self.filename, "rb") as f:
            for line in f:
                user, status = line.split(b':', 1)
                user = user.strip()
                status = status.strip()
                self.users[user] = status
        self.call = reactor.callLater(30, self._read)
        
    def startService(self):
        self._read()
        service.Service.startService(self)
    
    def stopService(self):        
        service.Service.stopService(self)
        self.call.cancel()
        
    def getUser(self, user):
        return defer.succeed(self.users.get(user, b"no such user"))
    
    def getFingerFactory(self):
        f = protocol.ServerFactory()
        f.protocol = FingerProtocol
        f.getUser = self.getUser
        return f
        
        
        
    
    
application = service.Application('finger', uid=1, gid=1)
f = FingerService('C:\\work\\users.txt')

finger = strports.service("tcp:79", f.getFingerFactory())

finger.setServiceParent(service.IServiceCollection(application))
f.setServiceParent(service.IServiceCollection(application))
        
        
    
    