import time
import socket
import struct

import numpy as np

TIM_HOST = '192.168.0.1'
TIM_PORT = 2111

TIM_STX = b'\x02'
TIM_ETX = b'\x03'

class LaserIP:
    def __init__( self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((TIM_HOST, TIM_PORT))
        self._buffer = b""
        self._timestamp = None
        self._scanData = None

    def __del__( self ):
        self.socket.close()

    def receive( self ):
        data = self._buffer
        while True:
            pos = data.find(TIM_ETX)
            if pos >= 0:
                break
            data = self.socket.recv(1024)
            self._buffer += data
        
        pos = self._buffer.find(TIM_ETX)
        assert( pos >= 0 )
        data = self._buffer[1:pos]
        self._buffer = self._buffer[pos+1:]
        return data

    def sendCmd( self, cmd ):
        data = TIM_STX + cmd + TIM_ETX
        self.socket.send(data)
        return self.receive()

    def internalScan( self ):
        data = self.sendCmd( b'sRN LMDscandata' ).split()
        timestamp = time.time()
        
        dist=[]
        dataStart = data.index("DIST1")+4
        dataEnd = dataStart + 3*271
        for i in data[dataStart:dataEnd]:
            dist.append(int(i,16))
        
        return timestamp, dist

    def startLaser( self ):
        return self.sendCmd( b'sMN LMCstartmeas' )

    def stopLaser( self ):
        self.sendCmd( b'sMN LMCstopmeas' )
        
class LaserDataAnalysis:
    def __init__(self):
        self.estop = np.load("TIM_estop.npy")
        self.warning = np.load("TIM_warning.npy")
        
    def check_ROIs(self, data):
        for i in range(len(data)-1):
            if(data[i] < self.estop[i]):
                return 2
            elif(data[i] < self.warning[i]):
                return 1
        return 0
        
