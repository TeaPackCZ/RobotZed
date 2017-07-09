
import zmq
import signal
import sys
from time import sleep
from Logger import Logger
import numpy as np

class gpsPoint:
    def __init__(self, x, y, e=10):
        self.x = x
        self.y = y
        self.Lat = x*np.pi/180.0
        self.Lon = y*np.pi/180.0
        self.Err = e

class gpsNavigation:
    def __init__(self,lenOfFilter):
        self.lengthOfFilter = lenOfFilter
        self.ItemKey = {"ID":0,"TIME":1,"LON":2,"LAT":3,"P_ERR":4,"DIR":5}
        self.IDKey = {"GPS1":0, "GPS2":1}

        p0 = gpsPoint(0,0)
        self.gpsPoints = [[],[]]
        for i in range(lenOfFilter):
            self.gpsPoints[0].append(p0)
            self.gpsPoints[1].append(p0)

        self.gpsWayPoint = gpsPoint(0,0)

        self.dir = np.zeros((2,self.lengthOfFilter),np.float)
        self.Time = [0,0]

    def shift(self,sensorID):
        for j in range(self.lengthOfFilter-2,-1,-1):
            self.gpsPoints[sensorID][j+1] = self.gpsPoints[sensorID][j]
            self.dir[sensorID,j+1] = self.dir[sensorID,j]

        self.gpsPoints[sensorID][0] = gpsPoint(0,0)
        self.dir[sensorID,0] = 0

    def update(self,sensorID,datastring):
        itemid,itemVal = datastring.split(":")
        if(itemid == "LON") or (itemid == "LAT"):
            pos,sign = itemVal.split(",")
            if(sign == "N") or (sign == "E"):
                ## Position on globe is from -180° to +180°
                itemVal = float(pos)
            else:
                itemVal = -float(pos)
        if(itemid == "LON"):
            self.gpsPoints[sensorID][0].Lon = itemVal
            return 0
        elif(itemid == "LAT"):
            self.gpsPoints[sensorID][0].Lat = itemVal
            return 0            
        elif(itemid == "P_ERR"):
            self.gpsPoints[sensorID][0].Err = float(itemVal)
            return 0
        elif(itemid == "DIR"):
            self.dir[sensorID,0] = int(itemVal)
            return 0
        elif(itemid == "TIME"):
            self.Time[sensorID] = float(itemVal)
            return 0
        elif(itemid == "ID"):
            return 0
        else:
            return -1

    def getDataString(self,sensorID):
        data  = "SensorID:" + str(sensorID)
        data += ";LON:" + str(self.gpsPoints[sensorID][0].Lon)
        data += ";LAT:" + str(self.gpsPoints[sensorID][0].Lat)
        data += ";P_ERR:" + str(self.gpsPoints[sensorID][0].PErr)
        data += ";DIR:" + str(self.dir[sensorID,0])
        data += ";TIME:" + str(self.Time[sensorID])
        return data

    def consistent(self):
        return (self.Time[0] == self.Time[1]) and (self.Time[0] > 1)

    def getCorrectedPosition(self):
        # get realdistance from points
        #   if(distance < dilutions:
        #       compute new position with higher precision
        #   else:
        #       compute new position with lower precision
        corX = (self.gpsPoints[0][0].x + self.gpsPoints[1][0].x) / 2.0
        corY = (self.gpsPoints[0][0].y + self.gpsPoints[1][0].y) / 2.0
        corErr = (self.gpsPoints[0][0].Err + self.gpsPoints[1][0].Err) / 2.0
        curPos = gpsPoint(corX,corY,corErr)
        return curPos

    def getDirAndDist(self,A,B):
        # You are at point A and want to go to point B
        dLat = B.Lat - A.Lat
        dLon = B.Lon - A.Lon

        R = 6378137.0

        distance = None
        angle = None

        ## Based on Orthrodromic navigation - see wiki
        alf = 2*np.arcsin(np.sqrt((np.sin((dLat)/2)**2
              +np.cos(B.Lat)*np.cos(A.Lat)*(dLon/2)**2)))

        angle = (np.arcsin((np.cos(B.Lat)*np.sin(dLon))/np.sin(alf))
                 /np.pi*180)%360

        if(dLat < 0):
            if(dLon < 0):
                angle -= 90
            elif(dLon>0):
                angle += 90
            else:
                angle += 180
        
        distance = np.round(alf*R)
        angle = np.round(angle)
        
        return distance,angle
        
class gpsModule:
    def __init__(self):
        
        self.logger = Logger("gpsNavigation")
        self.InPorts = ["10101","10102","10300"]
        self.OutPorts = ["10111"]
        self.enabled = True
        signal.signal(signal.SIGINT, self.sigINT_Handler)
        zMQC = zmq.Context()
        self.subscriber = zMQC.socket(zmq.SUB)
        self.publisher = zMQC.socket(zmq.PUB)

        self.GPSData = gpsNavigation(5)
        self.WayPoint = gpsPoint(0,0,0)
        self.waypointSet = False

        for port in self.InPorts:
            self.subscriber.connect('tcp://127.0.0.1:'+port)
            self.logger.save_line("Binded to port: " + port)
        self.subscriber.setsockopt(zmq.SUBSCRIBE, b"")

        for port in self.OutPorts:
            self.publisher.bind('tcp://127.0.0.1:'+port)
            self.logger.save_line("Connected to port: " + port)
        
        sleep(0.5)

    def sigINT_Handler(self, signal, frame):
        print("\ngpsNavigation detected SigINT signal")
        self.logger.save_line("Signal SigINT detected")
        self.enabled = False
        for port in self.InPorts:
            self.subscriber.disconnect('tcp://127.0.0.1:'+port)
            self.logger.save_line("SUB Disconnected from local port: " + port)
        for port in self.OutPorts:
            self.publisher.disconnect('tcp://127.0.0.1:'+port)
            self.logger.save_line("PUB Disconnected from local port: " + port)
        sys.exit(0)

    def updateData(self,line):
        lineSplit = line.split(";")
        gpsid = lineSplit[0].split(":")[1]
        if(gpsid in self.GPSData.IDKey):
            gpid = self.GPSData.IDKey[gpsid]
            self.GPSData.shift(gpid)
            for item in lineSplit:
                if(self.GPSData.update(gpid,item) == -1):
                   self.logger.save_line("Unsupported sentence : <"
                                         + item + ">")

    def updateWayPoint(self,line):
        lineSplit = line.split(";")
        self.WayPoint = gpsPoint(
                          float(lineSplit[1].split(":")[1])
                        , float(lineSplit[2].split(":")[1])
                        , float(lineSplit[3].split(":")[1]) )
        self.waypointSet = True
    
    def run(self):
        while(self.enabled):
            message = self.subscriber.recv_string()
            if(message.find("ID:GPS")>=0):
                self.updateData(message)
                if(self.GPSData.consistent()):
                    # watchdog = 0
                    if(self.waypointSet):
                        A = self.GPSData.getCorrectedPosition()
                        dist,azim = self.GPSData.getDirAndDist(A,self.WayPoint)
                        self.publisher.send_string("ID:NAV;DIST:"+str(dist)
                                                   +";AZIM:"+str(azim))
                    else:
                        A = self.GPSData.getCorrectedPosition()
                        self.logger.save_line("New position: LON: "
                                              + str(A.lon) + " LAT: "
                                              + str(A.lat))
            elif(message.find("ID:MAIN")>=0):
                self.updateWayPoint(message)
            else:
                self.logger.save_line("Ignoring sentense: <" + message + ">")
                # watchdog ++
                # if watchdog >= FiltLen:
                #   GPSdata.useOneSourceOnly == True
                # else:
                #   pass (wait for next update)
                sleep(0.0001)
