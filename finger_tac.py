# Read username, output from non-empty factory, drop connections
# Use deferreds, to minimi...

from twisted.application import service, strports
from twisted.internet import protocol, reactor, defer
from twisted.protocols import basic
from twisted.web import resource, server, static
import cgi



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

class FingerResource(resource.Resource):
    
    def __init__(self, users):
        self.users = users
        resource.Resource.__init__(self)
 
        

    def render_GET(self, request):
        print("please get me..")
        return "<html>Hello, world!</html>"
    
    def getChild(self, path, request):
        """
        'username is L{bytes}
        'request' is a 'twisted.web.server.Request
        """
        username = path
   
        messagevalue = self.users.get(username)
   
        if messagevalue:
            messagevalue = messagevalue.decode("ascii")
        if username:
            username = username.decode("ascii")
            
   
        username = cgi.escape(username)
        
        if messagevalue is not None:
            messagevalue = cgi.escape(messagevalue)
            text = '<h1>{}</h1><p>{}</p>'.format(username, messagevalue)
        else:            
            text = '<h1>{}</h1><p>no such user</p>'.format(username)
        text = text.encode("ascii")
        print("The final text is : ", text)
        return static.Data(text, 'text/html')
    
class FingerService(service.Service):
    def __init__(self, filename):
        self.filename = filename
        self.users = {}
        
    def _read(self):
        
        self.users.clear()
        with open(self.filename, "rb") as f:
            for line in f:
                user, status = line.split(b':', 1)
                user = user.strip()
                status = status.strip()
                self.users[user] = status
        self.call = reactor.callLater(30, self._read)
        
    def getUser(self, user):
        return defer.succeed(self.users.get(user, b"no such user"))
    
    def getFingerFactory(self):
        f = protocol.ServerFactory()
        f.protocol = FingerProtocol
        f.getUser = self.getUser
        return f
    
    def getResource(self):
        r = FingerResource(self.users)
        return r
        
    def startService(self):
        self._read()
        service.Service.startService(self)
        
    def stopService(self):
        service.Service.stopService(self)
        self.call.cancel()


application = service.Application('finger', uid=1, gid=1)
f = FingerService('c:/work/users.txt')
serviceCollection = service.IServiceCollection(application)
f.setServiceParent(serviceCollection)
strports.service("tcp:79", f.getFingerFactory()
                 ).setServiceParent(serviceCollection)
strports.service("tcp:8000", server.Site(f.getResource())
                 ).setServiceParent(serviceCollection)
        
            
        
        
    