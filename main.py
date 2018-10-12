from Logger import Logger
import signal
import sys
from time import sleep
import zmq

class master:
    def __init__(self):
        self.logger = Logger("mainLog")

        self.InPorts = ["10105","10201","10301","10501"]
        self.OutPortGPS = "10110"
        self.OutPortMBED = "10210"

        # If reverseRobot is False, robot drives with display in front
        # when True, robot drives with display on its tail.
        self.reverseRobot = True

        self.enabled = True
        signal.signal(signal.SIGINT, self.sigINT_Handler)
        zMQC = zmq.Context()

        self.subscriber = zMQC.socket(zmq.SUB)

        for port in self.InPorts:
            self.subscriber.connect('tcp://127.0.0.1:'+port)
            self.logger.save_line("Connected to port: " + port)
        self.subscriber.setsockopt(zmq.SUBSCRIBE, b"")

        self.publisherGPS = zMQC.socket(zmq.PUB)
        self.publisherGPS.connect('tcp://127.0.0.1:'+self.OutPortGPS)
        self.logger.save_line("PublisherGPS connected to port: " + self.OutPortGPS)

        self.publisherMBED = zMQC.socket(zmq.PUB)
        self.publisherMBED.connect('tcp://127.0.0.1:'+self.OutPortMBED)
        self.logger.save_line("PublisherMBED connected to port: " + self.OutPortMBED)
        
        sleep(0.5)
        # LIDAR related
        self.speedCoefs = [1.0, 0.5, 0.0]
        self.lidarSpeedCoef = 0.0
        
    def sigINT_Handler(self, signal, frame):
        print("\nMaster detected SigINT signal")
        self.logger.save_line("Signal SigINT detected")
        self.enabled = False
        
    def deinit(self):
        for port in self.InPorts:
            self.subscriber.disconnect('tcp://127.0.0.1:'+port)
            self.logger.save_line("SUB disconnected from local port: " + port)
        
        self.publisherGPS.disconnect('tcp://127.0.0.1:'+self.OutPortGPS)
        self.logger.save_line("PUB_GPS disconnected from local port: " + self.OutPortGPS)

        self.publisherMBED.disconnect('tcp://127.0.0.1:'+self.OutPortMBED)
        self.logger.save_line("PUB_MBED disconnected from local port: " + self.OutPortMBED)

    def SetWaypoint(self,data):
        self.publisherGPS.send_string(data)

    def checkAll(self):
        msg = ""
        oldmsg = " "
        waitingMSG = self.subscriber.poll(100,zmq.POLLIN)
        print("Waiting msgs: " +str(waitingMSG))
        while(waitingMSG > 0):
            msg = self.subscriber.recv_string()
            self.logger.save_line("RECIVED: " + msg)
            self.parseMessage(msg)
            waitingMSG = self.subscriber.poll(100,zmq.POLLIN)

    def parseMessage(self,data):
        [device,item,ID,state] = data.split(",")
        if(device == "gamePad"):
            if(item == "BTN"):
                if( ID == 2 ): ## RED B button
                    self.btn_B_pressed(state)
                elif( ID == 1): ## Green A button
                    self.btn_A_pressed(state)
                elif( ID == 8): ## BACK button
                    self.btn_back_pressed(state)
                elif( ID == 9): ## START button
                    self.btn_start_pressed(state)
            if(item == "AXS"):
                ids = ID.split(";")
                values = state.split(";")
                if(ids[0] == "0"):
                    self.send_diff_move(values[0], values[1])
        if(device == "laser"):
            if(item == "ROI"):
                self.lidarSpeedCoef = self.speedCoefs[state]
        return 0

    def btn_B_pressed(self):
        print ("Stop robot ... ")
        self.publisherMBED.send_string("$setD,M,0,0\r\n")

    def btn_A_pressed(self):
        print ("Start autonomous program")
        #subprocess.call("./zmq_init.sh")

    def btn_back_pressed(self):
        print ("Terminate program")
        # Turn motors off
        self.publisherMBED.send_string("$setD,M,0,0,\r\n")
        # Turn controlled off
        # HW restart pin not connected yet, ireversible.
        self.publisherMBED.send_string("$setD,T,0,0,\r\n")
        # Terminate all other modules of robot?
        #self.global_publisher.send_string("ID:ALL,ACTION:Terminate,\r\n")
        self.enabled = False

    def btn_start_pressed(self):
        print ("Enable robot ... ")
        # Soft restart of controller
        self.publisherMBED.send_string("$setD,C,1,1\r\n")
        sleep(5)
        # Enabling motors
        self.publisherMBED.send_string("$setD,M,1,1\r\n")

    def send_diff_move(self, value1 = 0.00, value0 = 0.00):
        ## Implemented lidar safety coeficients
        value_0 = int(value0*self.lidarSpeedCoef*100.0)
        value_1 = int(value1*self.lidarSpeedCoef*100.0)
        if(self.reverseRobot):
            message = ("$setM,D," + str(value_0*(-1))
                    + "," + str(value_1*(-1)) + "\r\n")
        else:
            message = ("$setM,D," + str(value_0)
                    + "," + str(value_1) + "\r\n")
        if(not self.disconnected):
            self.publisherMBED.send_string(message)

    def initRobot(self):
        sleep(1)
        #self.publisherGPS.send_string("ID:GPS1;RESTART:COLDSTART")
        #self.publisherGPS.send_string("ID:GPS2;RESTART:COLDSTART")
        sleep(1)

    def Game(self):
        waypoints = []

        #Load waypoints
        waypoints.append("ID:MAIN;LON:14.1471803;LAT:49.3101150;ERR:3")
        waypoints.append("ID:MAIN;LON:14.1511122;LAT:49.3083453;ERR:3")
        
        self.initRobot()
        #WaitForStartingWindow (if any)
        for waypoint in waypoints:
            self.SetWaypoint(waypoint)
            atWaypoint = False
            while(not atWaypoint and self.enabled):
                self.checkAll()
                sleep(0.1)
        #       updateAll
        #   MarkWaypoint/Goal
        #Play4Winner
        #Switch to manual
        self.deinit()
    
M = master()
M.Game()
