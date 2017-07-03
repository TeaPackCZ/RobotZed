import time

class Logger():
    def __init__(self, name = "defaultLogFile"):
        timestamp = time.strftime('%Y_%m_%d-%H_%M_%S')
        self.name = "Logs/" + timestamp + "_" + name + ".txt"
        try:
            self.logfile = open(self.name, 'w')
            self.opened = True
        except:
            self.opened = False

    def save_line(self,data):
        time_s = time.time()
        time_ms = str(int((time_s - int(time_s))*1000.0)).zfill(3)
        timestamp = (time.strftime(('%H_%M_%S'), time.localtime(time_s))
                     +"_"+ time_ms +" : ")
        if(self.opened):
            data = data.replace("\r","").replace("\n","")
            self.logfile.write(timestamp+data+"\r\n")
            self.logfile.flush()
            return 0,""
        else:
            return 1,str(timestamp+data)

    def close(self):
        if(self.opened):
            self.logfile.flush()
            self.logfile.close()
            self.opened = False
            return 0
        else:
            return 1

import zmq
import signal
import sys
from time import sleep

class zMQLogger():
    def __init__(self):
        self.logger = Logger("zMQ_logger")
        self.ports = ["10000"]
        self.externalIPs = []
        self.enabled = True
        signal.signal(signal.SIGINT, self.sigINT_Handler)
        zMQC = zmq.Context()
        self.subscriber = zMQC.socket(zmq.SUB)
        for port in self.ports:
            self.subscriber.connect('tcp://127.0.0.1:'+port)
            self.logger.save_line("Connected to port: " + port)
        self.subscriber.setsockopt(zmq.SUBSCRIBE, b"")

    def sigINT_Handler(self, signal, frame):
        print("\nZMQLogger detected SigINT signal")
        self.logger.save_line("Signal SigINT detected")
        for port in self.ports:
            self.subscriber.disconnect('tcp://127.0.0.1:'+port)
            self.logger.save_line("Disconnected from local port: " + port)
        for externalIP in self.externalIPs:
            self.subscriber.disconnect('tcp://'+externalIP)
            self.logger.save_line("Disconnected from IP: " + externalIP)
        self.enabled = False
        sys.exit(0)

    def addLocalPort(self,newport):
        if(self.enabled):
            if(newport in self.ports):
                self.logger.save_line("LocalPort " + newport + " is already binded...")
            else:
                self.ports.append(newport)
                self.subscriber.connect('tcp://127.0.0.1:'+newport)
                self.logger.save_line("Connected to new local port: " + newport)

    def addIP(self, newIP):
        if(self.enabled):
            if(newIP in self.externalIPs):
                self.logger.save_line("Adress:Port " + newIP + " is already connected...")
            else:
                try:
                    self.subscriber.connect('tcp://'+newIP)
                    self.logger.save_line("Connected to new adress:port: " + newIP)
                    self.externalIPs.append(newIP)
                except:
                    self.logger.save_line("New adress can't be connected - IP "
                                          + newIP + " not reachable")

    def run(self):
        while(self.enabled):
            message = self.subscriber.recv_string()
            self.logger.save_line(message)


