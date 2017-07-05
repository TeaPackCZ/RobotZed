from Logger import Logger
import signal
import sys
from time import sleep
import zmq

class master:
    def __init__(self):
        self.logger = Logger("mainLog")

        self.InPorts = ["10111","10201"]
        self.OutPorts = ["10301","10202"]

        self.enabled = True
        signal.signal(signal.SIGINT, self.sigINT_Handler)
        zMQC = zmq.Context()

        self.subscriber = zMQC.socket(zmq.SUB)

        for port in self.InPorts:
            self.subscriber.connect('tcp://127.0.0.1:'+port)
            self.logger.save_line("Binded to port: " + port)
        self.subscriber.setsockopt(zmq.SUBSCRIBE, b"")

        #self.poller = zmq.Poller()
        #self.poller.register(self.subscriber, zmq.POLLIN)

        self.publisher = zMQC.socket(zmq.PUB)

        for port in self.OutPorts:
            self.publisher.bind('tcp://127.0.0.1:'+port)
            self.logger.save_line("Connected to port: " + port)
        
        sleep(0.5)
        
    def sigINT_Handler(self, signal, frame):
        print("\nMaster detected SigINT signal")
        self.logger.save_line("Signal SigINT detected")
        self.enabled = False
        for port in self.InPorts:
            self.subscriber.disconnect('tcp://127.0.0.1:'+port)
            self.logger.save_line("SUB Disconnected from local port: " + port)
        for port in self.OutPorts:
            self.publisher.disconnect('tcp://127.0.0.1:'+port)
            self.logger.save_line("PUB Disconnected from local port: " + port)
        sys.exit(0)

    def SetWaypoint(self,data):
        self.publisher.send_string(data)

    def checkAll(self):
        msg = ""
        oldmsg = " "
        waitingMSG = self.subscriber.poll(100,zmq.POLLIN)
        print("Waiting msgs: " +str(waitingMSG))
        while(waitingMSG > 0):
            msg = self.subscriber.recv_string()
            waitingMSG = self.subscriber.poll(100,zmq.POLLIN)
            print("New msg: " + msg)
        print("Everything checked ^.^")

    def Game(self):
        waypoints = []

        #Load waypoints
        waypoints.append("ID:MAIN;LON:14.1471803;LAT:49.3101150;ERR:3")
        waypoints.append("ID:MAIN;LON:14.1511122;LAT:49.3083453;ERR:3")
        
        #WaitForSync
        #WaitForStartingWindow (if any)
        for waypoint in waypoints:
            self.SetWaypoint(waypoint)
            while(!atWaypoint)
                self.checkAll()
                sleep(0.2)
        #       updateAll
        #   MarkWaypoint/Goal
        #Play4Winner
        #Switch to manual
    
M = master()
M.Game()
