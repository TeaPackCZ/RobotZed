﻿
import zmq
import signal
import sys
from time import sleep
from Logger import Logger
import numpy as np

class gpsNavigation:
    def __init__(self,lenOfFilter):
        self.lengthOfFilter = lenOfFilter
        self.ItemKey = {"ID":0,"TIME":1,"LON":2,"LAT":3,"P_ERR":4,"DIR":5}
        self.IDKey = {"GPS1":0, "GPS2":1}
        
        self.Lon = np.zeros((2,self.lengthOfFilter),np.float)
        self.Lat = np.zeros((2,self.lengthOfFilter),np.float)
        self.PErr = np.zeros((2,self.lengthOfFilter),np.float)
        self.dir = np.zeros((2,self.lengthOfFilter),np.float)
        
        self.Time = [0,0]

    def shift(self,sensorID):
        for j in range(self.lengthOfFilter-2,-1,-1):
            self.Lon[sensorID,j+1] = self.Lon[sensorID,j]
            self.Lat[sensorID,j+1] = self.Lat[sensorID,j]
            self.PErr[sensorID,j+1] = self.PErr[sensorID,j]
            self.dir[sensorID,j+1] = self.dir[sensorID,j]

        self.Lon[sensorID,0] = 0
        self.Lat[sensorID,0] = 0
        self.PErr[sensorID,0] = 0
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
            self.Lon[sensorID,0] = itemVal
            return 0
        elif(itemid == "LAT"):
            self.Lat[sensorID,0] = itemVal
            return 0            
        elif(itemid == "P_ERR"):
            self.PErr[sensorID,0] = float(itemVal)
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
        data += ";LON:" + str(self.Lon[sensorID,0])
        data += ";LAT:" + str(self.Lat[sensorID,0])
        data += ";P_ERR:" + str(self.PErr[sensorID,0])
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
        corLat = np.mean(self.Lat,0)[0]
        corLon = np.mean(self.Lon,0)[0]
        corErr = np.mean(self.PErr,0)[0]
        return corLon,corLat,corErr


    def getDirAndDist(self,waypoint):
        curLat,curLon,curErr = self.getCorrectedPosition()
        dLat = waypoint[0] - curLat
        dLon = waypoint[1] - curLon

        distance = None
        angle = None

        if(abs(dLat) < 0.5) and (abs(dLon) < 0.5):
            LongitudeRadius = np.cos(curLat/180.0*np.pi)*6378137.0 # [m]
            LonDegreseLength = LongitudeRadius*2*np.pi/360.0
            LatDegreseLength = np.pi*np.sqrt(2*(6378137.0**2+6356752.3**2))/360.0

            dLatMetric = dLat * LatDegreseLength
            dLonMetric = dLon * LonDegreseLength

            angle = round(np.arctan(dLatMetric/dLonMetric)/np.pi*180);
            distance = np.hypot(dLatMetric,dLonMetric)
        
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
        self.WayPoint = np.zeros((3),np.float)
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
        self.WayPoint = [ float(lineSplit[1].split(":")[1])
                        , float(lineSplit[2].split(":")[1])
                        , float(lineSplit[3].split(":")[1]) ]
        self.waypointSet = True
    
    def run(self):
        while(self.enabled):
            message = self.subscriber.recv_string()
            if(message.find("ID:GPS")>=0):
                self.updateData(message)
                if(self.GPSData.consistent()):
                    # watchdog = 0
                    if(self.waypointSet):
                        dist,azim = self.GPSData.getDirAndDist(self.WayPoint)
                        self.publisher.send_string("ID:NAV;DIST:"+str(dist)
                                                   +";AZIM:"+str(azim))
                    else:
                        lon,lat,err = self.GPSData.getCorrectedPosition()
                        self.logger.save_line("New position: LON: "
                                              + str(lon) + " LAT: "
                                              + str(lat))
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

C = gpsModule()
C.run()