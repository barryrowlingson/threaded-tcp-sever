import random
import string

from PyQt4 import QtCore
from PyQt4.QtNetwork import QTcpServer, QTcpSocket, QHostAddress
from PyQt4.QtCore import QObject


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
