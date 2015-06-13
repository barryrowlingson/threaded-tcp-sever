import random
import string
import threading

from PyQt4 import QtCore
from PyQt4.QtNetwork import QTcpServer, QTcpSocket, QHostAddress
from PyQt4.QtCore import QObject, QTimer
from baseserver import Server

APPLOCK = threading.Lock()

class ThreadedServer(Server):
    def __init__(self, listen_port, parent = None):
        Server.__init__(self, listen_port, parent)   
        
        # define verbose variable
        self.verbose = False
      
    # re-implement  'readSocket' method
    @QtCore.pyqtSlot(str)
    def readSocket(self, socket_id):
        """
        Handles a write event from a client.
        """
        try:
            # Takes the socket from the dictionary, using the socket_id, then read the data.
            readysocket = self.sockets.get(str(socket_id))
            #readysocket = self.sockets.get(socket_id)
            #print ("socket id: " + socket_id)
            #print (self.sockets.has_key(str(socket_id)))
            #print (self.sockets)

            socket_info = readysocket.readAll()
            
            if self.verbose:
				print ("[*] Socket '%s' sent data: %s" % ( socket_id, socket_info.data()) )
            
            # Create a thread for handling the data, emit 'ready' when done inside run(), 
            # so 'socketReady' gets called.
            socket_thread = ThreadAction(socket_info, socket_id)
            socket_thread.signaler.ready.connect(self.socketReady)
            socket_thread.start()
            
        except KeyError:
            print ('[*] Error, socket not in queue.')

class ThreadAction(threading.Thread):
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
        self.ready.emit(socket_id, text)
        
