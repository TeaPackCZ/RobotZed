from Logger import Logger
import signal
import sys
from time import sleep
import zmq
import serial

class mbed:
    def __init__(self):
        self.logger = Logger("MbedLog")

        self.InPorts = ["10210"]
        self.OutPorts = ["10201"]

        self.enabled = True
        self.connected = False
        signal.signal(signal.SIGINT, self.sigINT_Handler)
        zMQC = zmq.Context()

        self.subscriber = zMQC.socket(zmq.SUB)

        for port in self.InPorts:
            self.subscriber.connect('tcp://127.0.0.1:'+port)
            self.logger.save_line("Binded to port: " + port)
            sleep(0.5)
        self.subscriber.setsockopt(zmq.SUBSCRIBE, b"")

        self.publisher = zMQC.socket(zmq.PUB)

        for port in self.OutPorts:
            self.publisher.bind('tcp://127.0.0.1:'+port)
            self.logger.save_line("Connected to port: " + port)
            sleep(0.5)

        self.get_args()
        self.connect_serial()
        
        sleep(0.5)

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
            self.zmqPort = str(sys.argv[3])

        if(len(sys.argv) >= 5):
            self.zmqID = str(sys.argv[4])

        print("Settings -> Serial: " + self.mserial + " speed: "
              + str(self.mbaud) + " ZMQ port: " + self.zmqPort
              + " ID: " + str(self.zmqID))

    def connect_serial(self):
        if not self.connected:
            if self.normalRun:
                try:
                    self.serial = serial.Serial(self.mserial, self.mbaud, timeout=0.05)
                    self.serial.bytesize = serial.EIGHTBITS
                    self.serial.parity = serial.PARITY_NONE
                    self.serial.stopbits = serial.STOPBITS_ONE
                    
                    self.conected = True
                    print( "Connected to " + self.mserial)
                
                    if(self.serial.readable()):
                        self.serial.flush()
                        self.serial.readline()

                    return True
                except:
                    print( "Failed connecting to " + self.mserial)
                    return False
            else:
                try:
                    logfile = open(self.mserial,'rb')
                    self.LogData = []
                    for line in logfile:
                        self.LogData.append(line)
                    logfile.close()
                    return True
                except:
                    self.logger.save_line("Opening log file <" + self.mserial
                                          +"> failed")
                    return False
     
    def sigINT_Handler(self, signal, frame):
        print("\nMbed detected SigINT signal")
        self.logger.save_line("Signal SigINT detected")
        self.enabled = False
        for port in self.InPorts:
            self.subscriber.disconnect('tcp://127.0.0.1:'+port)
            self.logger.save_line("SUB Disconnected from local port: " + port)
        for port in self.OutPorts:
            self.publisher.disconnect('tcp://127.0.0.1:'+port)
            self.logger.save_line("PUB Disconnected from local port: " + port)
        if not self.connected:
            self.connected = False
            self.serial.flush()
            self.serial.close()
            self.logger.save_line("Serial on " + self.mserial + " disconnected.")
        sys.exit(0)
        
    def recvUpdate(self):
        waitingMSG = self.subscriber.poll(100,zmq.POLLIN)
        while(waitingMSG > 0):
            message = self.subscriber.recv_string()
            self.parse_zmq_message(message)
            waitingMSG = self.subscriber.poll(100,zmq.POLLIN)

        if(self.serial.readable()):
            message = self.serial.readline()
            self.parse_serial_message(message)

    def parse_zmq_message(self,data):
        self.logger.save_line("Receives ZMQ message: <" + data + ">")
        self.msgToWrite = data
        self.toWrite = True

    def parse_serial_message(self,data):
        self.logger.save_line("Receives serial message: <" + data + ">")
        
    def run(self):
        self.logger.save_line("mbed loop started...")
        print "Waitin for update..."
        self.toWrite = False
        sleep(1)
        while(self.enabled):
            self.recvUpdate()
            if(self.toWrite):
                self.serial.write(self.magToWrite)
            sleep(0.1)

M = mbed()
M.run()

