import random
import string
#import threading

from PyQt4 import QtCore
from PyQt4.QtNetwork import QTcpServer, QTcpSocket, QHostAddress
from PyQt4.QtCore import QObject#, QTimer

#APPLOCK = threading.Lock()

class Server(QTcpServer):
    def __init__(self, listen_port, parent = None):
        QTcpServer.__init__(self, parent)   
        
        # define verbose variable
        self.verbose = True
        
        # Starts listening on selected port.
        try:
            port = int(listen_port)
        except:
            print ('[*] Error, port is not a number.')
				
        started = self.listen(address = QHostAddress.Any, port = port)
        
        # It is possible that such port is not available.
        if started:
            print ('[*] Listening on port %s' % port)
            
        else:
            print ('[*] Could not bind port %s' % port)
        
        # This dictionary will always contains a reference to all 
        #current sockets.
        self.sockets = {}
            
    def incomingConnection(self, socket_descriptor):
        """
        This method is automatically called by Qt when 
        a peer has connected.   
        """
    
        # Constructs a Socket object with the socket_descriptor
        # passed by Qt, and connects some of it signals to 
        # slots in this class.
        newsocket = Socket(self)
        newsocket.setSocketDescriptor(socket_descriptor)
        newsocket.readyReadId.connect(self.readSocket)
        newsocket.disconnectedId.connect(self.closeSocket)
     
        # Generates a random string in order to tell sockets apart, and make sure it's unique.
        rand_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(3))
        
        while rand_id in self.sockets.keys():
            rand_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(3))
        
        # Keeps a reference to this socket on the 'sockets' dictionary, the random string is the key.
        # Also set the key to the Socket object.
        self.sockets[rand_id] = newsocket
        newsocket.setId(rand_id)
        
        if self.verbose:
			print('[*] New incoming connection %s from ip %s' % (rand_id, newsocket.peerAddress().toString()))
        
    @QtCore.pyqtSlot(str)
    def readSocket(self, socket_id):
        """
        Handles a write event from a client.
        """
        print ("[*] This method needs to be re-implemented by the inheriting class" )
        
        try:
            # Takes the socket from the dictionary, using the socket_id, then read the data.
            readysocket = self.sockets.get(str(socket_id))
            socket_info = readysocket.readAll()
            
            if self.verbose:
				print ("[*] Socket '%s' sent data: %s" % ( socket_id, socket_info.data()) )
            
            # Create a thread for handling the data, emit 'ready' when done inside run(), 
            # so 'socketReady' gets called.
            #socket_thread = ThreadAction(socket_info, socket_id)
            #socket_thread.signaler.ready.connect(self.socketReady)
            #socket_thread.start()
            
        except KeyError:
            print ('[*] Error, socket not in queue.')

    @QtCore.pyqtSlot(str)
    def closeSocket(self, socket_id):
        """
        Handles a socket disconnection.
        """
        try:
            closedsocket = self.sockets.pop(socket_id)
                 
            print ('[*] Socket closed: %s' % socket_id)
    
        except KeyError:
            print ('[*] Error, socket not in queue.')
          
    @QtCore.pyqtSlot(str, str)
    def socketReady(self, socket_id, text):
        """
        Triggered from the threads when they are done
        """
        try:            
            # The following lines are for clean up purposes. Uncomment only
            # if you want to close the socket.
            '''
            in_socket = self.sockets.pop(socket_id)
            self.connect(in_socket, QtCore.SIGNAL('bytesWritten()'), in_socket, QtCore.SLOT('deleteLater()'))
            '''
	            
            # Uncomment the following line if you want to write something back 
            # to the peer.
            #in_socket.write("Reply")
            
            print ("Message: '%r' from socket %s has been processed." % (str(text), socket_id))
            
        except KeyError:
            print ('Error, socket not in queue.')
          
class Socket(QTcpSocket):
    readyReadId = QtCore.pyqtSignal((str,))
    disconnectedId = QtCore.pyqtSignal((str,))
    
    def __init__(self, parent = None):
        QTcpSocket.__init__(self, parent)
        
        # The 'readyRead' signal is from QTcpSocket, call 'readyReadId' 
        # whenever is emitted.
        self.readyRead.connect(self.onReadyRead)
        self.disconnected.connect(self.onDisconnected)
    
    def setId(self, socket_id):
        self.id = socket_id
        
    @QtCore.pyqtSlot()
    def onReadyRead(self):
        """
        Re-emits a ready signal that sends the ID, so the Server knows
        which socket is ready.
        """
        self.readyReadId.emit(self.id)

    @QtCore.pyqtSlot()
    def onDisconnected(self):
        """
        Re-emits a ready signal that tells the server that the client
        closed the socket.
        """
        self.disconnectedId.emit(self.id)

'''class ThreadAction(threading.Thread):
    """
    Thread class based on Python's standard threading class.
    """
    def __init__(self, socket_info, socket_id):
        threading.Thread.__init__(self)
        
        # Includes the unique id and the message.
        self.socket_id = socket_id
        self.socket_info = socket_info
        
        # QObject object for signaling purposes. 
        self.signaler = Signaler()
    
    def run(self):
        ##APPLOCK.acquire()
        
        ##
        ## Do something with the socket_info (message) 
        ## and don't forget to signal 'ready'.
        ##
        
        # Passing the socket_id as first parameter is mandatory, 
        # second argument can be any string.
        self.signaler.signalReady(self.socket_id, self.socket_info.data().decode("utf-8"))
        ##APPLOCK.release()

class Signaler(QObject):
    """
    Class for using QObject signals to communicate 
    threads with main program.
    """
    ready = QtCore.pyqtSignal((str, str,))
    
    def __init__(self, parent = None):
        QObject.__init__(self, parent)
     
    def signalReady(self, socket_id, text):
        self.ready.emit(socket_id, text)'''
        
