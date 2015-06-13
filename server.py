#!/usr/bin/python3

import sys
#import signal

from PyQt4.QtCore import QCoreApplication

from threadedserver import ThreadedServer

def exit_handler(*args):
    print ('Exiting!')
    sys.exit(0)

if __name__ == '__main__':
    app = QCoreApplication(sys.argv)
    server = ThreadedServer(listen_port=32000)
    
    #signal.signal(signal.SIGINT, exit_handler)
    sys.exit(app.exec_())
    

