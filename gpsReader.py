
import serial   # apt install python-serial
import zmq      # apt install python-zmq
from Logger import Logger

import signal
import sys
from time import sleep

class gpsReader():

    def __init__(self):
        self.disconected = True
        self.enabled = True
        self.manSerial = False
        self.normalRun = True

        self.ToWrite = False

        self.serBaud = 38400
        self.zmqOutPort = "10100"
        self.zmqInPort = "10300"
        self.mserial = ""
        self.zmqID = "defaultGPS"

        self.parsedVTG = -1
        self.parsedGGA = -1
        self.parsedGLL = -1

        self.pos_err = -1
        
        self.get_args()

        zmq_cont = zmq.Context()
        self.publisher = zmq_cont.socket(zmq.PUB)
        self.subscriber = zmq_cont.socket(zmq.SUB)

        signal.signal(signal.SIGINT, self.sigINT_Handler)
        self.logger = Logger(self.zmqID)
        
        if(self.connect_serial() and self.connect_zmq()):
            self.main_loop()

    def sigINT_Handler(self, signal, frame):
        print (self.zmqID + " detected SigINT signal")
        self.logger.save_line("Signal SigINT detected")
        self.enabled = False
        self.publisher.disconnect('tcp://127.0.0.1:'+str(self.zmqOutPort))
        if self.normalRun:
            self.ser.close()
        self.logger.close()
        sys.exit(0)

    def get_args(self):
        if(len(sys.argv) < 2):
            print ("Usage: " + str(sys.argv[0]) + " <PATH TO TTY PORT>" +
                   "[opt: <BaudRate> <ZMQPort> <ID>]" )
            print ("Secondary use: " + str(sys.argv[0])
                   + " <PATH TO RAW LOGFILE>")
            sys.exit(0)
    
        if(len(sys.argv) >= 2):
            self.mserial = sys.argv[1]
            if(sys.argv[1].find("/dev/") >= 0):
                #normal run from physical device
                self.normalRun = True
            elif(sys.argv[1].find("Logs/") >= 0):
                # Run from LOG
                self.normalRun = False
            
        if(len(sys.argv) >= 3):
            self.mbaud = int(sys.argv[2])

        if(len(sys.argv) >= 4):
            self.zmqOutPort = str(sys.argv[3])

        if(len(sys.argv) >= 5):
            self.zmqID = str(sys.argv[4])

        print("Settings -> Serial: " + self.mserial + " speed: "
              + str(self.mbaud) + " ZMQ port: " + self.zmqOutPort
              + " gps ID: " + str(self.zmqID))
       
    def connect_serial(self):
        if self.disconected:
            if self.normalRun:
                try:
                    self.ser = serial.Serial(self.mserial, self.mbaud)
                    self.ser.bytesize = serial.EIGHTBITS
                    self.ser.parity = serial.PARITY_NONE
                    self.ser.stopbits = serial.STOPBITS_ONE
                    
                    self.disconected = False
                    print( "Connected to " + self.mserial)
                
                    if(self.ser.readable()):
                        self.ser.flush()
                        self.ser.readline()

                    return True
                except:
                    print( "Failed connecting to " + self.mserial)
                    return False
            else:
                try:
                    logfile = open(self.mserial,'rb')
                    self.LogData = []
                    for line in logfile:
                        if(line.find("$")>=0):
                            if(line.find(" : ")>=0):
                                splt = line.split(" : ")
                                self.LogData.append(splt[1])
                            else:
                                self.LogData.append(line)
                    logfile.close()
                    return True
                except:
                    self.logger.save_line("Opening log file <" + self.mserial
                                          +"> failed")
                    return False
 
    def connect_zmq(self):
        try:
            self.publisher.bind('tcp://127.0.0.1:'+str(self.zmqOutPort))
            self.logger.save_line("Binded to local port: " + self.zmqOutPort)
            self.publisher.send_string(self.zmqID + " binded on port "
                                       + self.zmqOutPort)
        except:
            self.logger.save_line("Failed to bind localPort "
                                  + self.zmqOutPort)
        try:
            self.subscriber.connect('tcp://127.0.0.1:'+self.zmqInPort)
            self.subscriber.setsockopt(zmq.SUBSCRIBE, b"")
            self.logger.save_line("Connected to local port: " + self.zmqInPort)
        except:
            self.logger.save_line("Failed to connect localPort "
                                  + self.zmqInPort)
            return False
        finally:
            sleep(1)
            return True


    def parseRMC(self,line):
        ## RMC message:
        #   Time fix,
        #   status (Active/Void)
        #   Latitude,N
        #   Longitude,E
        #   Speed over ground (Kn)
        #   Track angle (true deg.)
        #   Date (DDMMYY)
        #   Magnetic variation
        return 10

    def parseVTG(self,line):
        ## VTG Message:
        #   True track made good
        #   Magnetic track made good
        #   Ground speed (Kn)
        #   Ground speed (km/h)
        try:
            datas = line.split(",")
            self.gps_dir = float(datas[1])
            self.gps_dir = int(self.gps_dir)
            return 0
        except:
            return 1

    def parseGGA(self,line):
        ## GGA message -
        #   Time fix,
        #   Latitude,N
        #   Longitude,E
        #   FixQuality
        #   NumberOfSatelites
        #   Horizontal dilution of position
        #   Altitude
        ##
        data_split = line.split(",")
        try: # to parse time:
            self.gps_time = data_split[1]
        except:
            return 4 # Parsing failed totally
        try: # to parse positon
            self.latitude = round(float(data_split[2])/100,7)
            self.longitude = round(float(data_split[4])/100,7)
            self.lat_ns = data_split[3]
            self.lon_we = data_split[5]
        except:
            return 3 #Time parsed, position failed
        try:
            self.pos_err = data_split[8]
        except:
            return 2 # Time and position parsed, pos.Error failed
        try:
            self.altitude = data_split[9]
            return 0 # Parsing succesfull
        except:
            return 1 # Time, position and posErr parsed, altitude failed

    def parseGLL(self,line):
        ## GLL message:
        #   Latitude,N
        #   Longitude,E
        #   time Fix
        #   Status (A/V - Active/Void)
        try:
            data_split = line.split(",")
            self.lat_ns = data_split[2]
            self.lon_we = data_split[4]
            self.longitude = round(float(data_split[3])/100,7)
            self.latitude = round(float(data_split[1])/100,7)
            self.gps_time = data_split[5]
            return 0
        except:
            self.lat_ns = " "
            self.lon_we = " "
            self.longitude = -1.0
            self.latitude = -1.0
            self.gps_time = -1.0
            try:
                if(float(data_split[5]) > 10):
                    self.gps_time = data_split[5]
                    return 1
            except:
                pass
            return 2
        
    def sendZMQPosition(self):
        data = "ID:"+str(self.zmqID)
        data+= ";TIME:"+str(self.gps_time)
        data+= ";LON:"+str(self.longitude)+","+self.lon_we
        data+= ";LAT:"+str(self.latitude)+","+self.lat_ns
        data+= ";P_ERR:"+str(self.pos_err)
        self.publisher.send_string(data)
        
    def sendZMQTime(self):
        data = "ID:"+str(self.zmqID)
        data+= ";TIME:"+str(self.gps_time)
        self.publisher.send_string(data)

    def sendZMQAll(self):
        data = "ID:"+str(self.zmqID)
        data+= ";TIME:"+str(self.gps_time)
        data+= ";LON:"+str(self.longitude)+","+self.lon_we
        data+= ";LAT:"+str(self.latitude)+","+self.lat_ns
        data+= ";P_ERR:"+str(self.pos_err)
        data+= ";DIR:"+str(self.gps_dir)
        self.publisher.send_string(data)

    def sortLine(self,line):
        ## drop data about satelites
        if(str(line).find("GSV,") == -1):
            self.logger.save_line(line)
            line = str(line)
            if(line.find("GNRMC") >= 0):
                ## first message from chunk - reset all parsed values
                self.parsedVTG = -1
                self.parsedGGA = -1
                self.parsedGLL = -1
                parsed = self.parseRMC(line)
            elif(line.find("$GNVTG")>=0):
                # VTG - minimal information about direction and speed
                self.parsedVTG = self.parseVTG(line)
            elif(line.find("$GNGGA") >= 0):
                # GGA - complex information about 3D position and pos.dilution
                # GGA is main source of needed information
                self.parsedGGA = self.parseGGA(line)
            elif(line.find("$GNGLL") >= 0):
                # GLL - minimal information about position
                self.parsedGLL = self.parseGLL(line)
                self.sendColected()

    def sendColected(self):
        ## possibilities:
        #   1) got only time
        #   2) got 1) + position and dilution of position
        #   3) got 2) + speed and direction
        if(self.parsedGGA == 3) or (self.parsedGLL == 1): # time only
            self.sendZMQTime()
        if(self.parsedGGA < 3): # Got position
            if(self.parsedVTG == 0): # Got speed and direction
                self.sendZMQAll()
            else:
                self.sendZMQPosition()
                
    def syncLog(self):
        for i in range(10):
            if(self.LogData[i].find("RMC") >= 0):
                return i

    def parseMessage(self, data):
        if(data.find(self.zmqID)>=0):
            split = data.split(";")
            for item in split:
                name,value = item.split(":")
                if(value.find("COLDSTART") >= 0):
                    self.ToWrite = True
                    self.MsgType = "COLD"
                elif(value.find("WARMSTART")>=0):
                    self.ToWrite = True
                    self.MsgType = "WARM"
                else:
                    self.logger.save_line("Unsupported message: <" +data
                                          + "> with argument: <" + value + ">")
        else:
            self.logger.save_line("Unrecognized message: <" +data+ ">")
                    

    def ColdStart(self):
        #msg = [0xB5, 0x62, 0x06, 0x04, 0x04, 0x00, 0xFF, 0xFF, 0x02, 0x00, 0x0E, 0x61]
        msg = 'B56206040400FFFF02000E61'
        self.logger.save_line("Cold start requested")
        if self.normalRun:
            success = self.ser.write(msg.decode("hex"))
        else:
            success = True
            self.logger.save_line("Message: <" + msg + ">")
        return success

    def WarmStart(self):
        #msg = [0xB5, 0x62, 0x06, 0x04, 0x04, 0x00, 0x01, 0x00, 0x02, 0x00, 0x11, 0x6C]
        msg = 'B5620604040001000200116C'
        self.logger.save_line("Warm start requested")
        if self.normalRun:
            success = self.ser.write(msg.decode("hex"))
        else:
            success = True
            self.logger.save_line("Message: <" + msg + ">")
        return success

    def writeMessage(self):
        self.ToWrite = False
        if(self.MsgType is "WARM"):
            self.WarmStart()
        elif(self.MsgType is "COLD"):
            self.ColdStart()
        else:
            self.logger.save_line("Unsupported message type: <" + self.MsgType + ">")

    def main_loop(self):
        if self.normalRun:
            while self.enabled:
                waitingMSG = self.subscriber.poll(20,zmq.POLLIN)
                while(waitingMSG > 0):
                    msg = self.subscriber.recv_string()
                    self.parseMessage(msg)
                    waitingMSG = self.subscriber.poll(20,zmq.POLLIN)
                if(self.ser.writable() and self.ToWrite):
                    self.writeMessage()
                if(self.ser.readable()):
                    line = self.ser.readline()
                    self.sortLine(line)
                sleep(0.0001)
            self.ser.close()
        else:
            lineIndex = self.syncLog()
            maxIndex = len(self.LogData)
            while(lineIndex < maxIndex):
                waitingMSG = self.subscriber.poll(20,zmq.POLLIN)
                while(waitingMSG > 0):
                    msg = self.subscriber.recv_string()
                    self.parseMessage(msg)
                    waitingMSG = self.subscriber.poll(20,zmq.POLLIN)
                if(self.ToWrite):
                    self.writeMessage()
                self.sortLine(self.LogData[lineIndex])
                if(self.LogData[lineIndex].find("GLL") >= 0):
                    sleep(0.1) ## corresponds to GPS settings (10Hz)
                lineIndex += 1
            self.enabled = False
            
        self.logger.close()

B = gpsReader()
B.main_loop()
