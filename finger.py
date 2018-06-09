from twisted.internet import protocol, reactor, defer, utils, endpoints
from twisted.protocols import basic

class FingerProtocol(basic.LineReceiver):
    def lineReceived(self, user):        
        d = self.factory.getUser(user)
        
        def onError(err):
            return 'internal error in server'
        d.addErrback(onError)
        
        def writeResponse(message):
            self.transport.write(b'We found it : ' + message + b'\r\n')
            print("Success!!")
            self.transport.loseConnection()
            
        d.addCallback(writeResponse)
            

class FingerFactory(protocol.ServerFactory):
    protocol = FingerProtocol
    
   # def __init__(self, users):
   #     self.users = users
        
    def getUser(self, user):
        return utils.getProcessOutput(b"finger", [user])
#        return utils.getProcessOutput(b"C:/work/TwistedFinger/dir.exe", [user])
    
fingerEndpoint = endpoints.serverFromString(reactor, "tcp:1079")
fingerEndpoint.listen(FingerFactory())
reactor.run()
