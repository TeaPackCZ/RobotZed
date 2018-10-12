import time
import socket
import struct

import numpy as np
import zmq
import signal
from time import sleep
from coord_lib import *

import matplotlib.pyplot as plt

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
        self.enabled = True

        self.zMQport = "10301"
        self.connected = False
        signal.signal(signal.SIGINT, self.sigINT_Handler)
        zMQC = zmq.Context()

        self.publisher = zMQC.socket(zmq.PUB)
        self.publisher.connect('tcp://127.0.0.1:'+self.zMQport)
        sleep(0.5)

        self.laser = LaserIP()

    def sigINT_Handler(self,signal,frame):
        print("\nLidar detected SigINT signal")
        self.enabled = False

    def deinit(self):
        self.publisher.disconnect("tcp://127.0.0.1:"+self.zMQport)
        del self.laser

    def check_ROIs(self, data):
        for i in range(len(data)-1):
            if(data[i] < self.estop[i]):
                return 2
            elif(data[i] < self.warning[i]):
                return 1
        return 0

    def run(self):
        while(self.enabled):
            [running, distance] = self.laser.internalScan()
            ang_values = np.asarray(distance, np.int16)
            
            ROIs = self.check_ROIs(ang_values)
            self.publisher.send_string("laser,ROI,all," + str(ROIs))

            #if(self.trackObject):
            segments = ang_segmentation(ang_values, max_diff = 100)
            
                

        self.deinit()

    def testrun(self):
        number_of_measurements = 1
        laser = LaserIP()
        
        drop = 10
        
        axis_x = np.arange(-135+drop,136,1/3.0,np.float)

        for i in range(number_of_measurements):
            [running, distance_raw] = laser.internalScan()
            distance = distance_raw[3*drop::]

            # Segmentation
            segments = ang_segmentation(distance, max_diff = 100)

            ## convert segments to cartezian:
            new_x = []
            new_y = []
            for j in range(len(segments)):
                [nx,ny] = ang2cartezian(axis_x[segments[j][0]:segments[j][0]+segments[j][1]],segments[j][2])
                new_x.append(nx)
                new_y.append(ny)

            ## Show data:
            plt.figure(2*i)
            #Angular data:
            for j in range(len(segments)):
                plt.plot(axis_x[segments[j][0]:segments[j][0]+segments[j][1]],segments[j][2])
            # Cartezian data:
            plt.figure(2*i+1)
            for j in range(len(segments)):
                plt.plot(new_x[j],new_y[j])
                plt.plot(0,0,'r*')
            plt.show()

A =LaserDataAnalysis()
A.testrun()
A.deinit()

