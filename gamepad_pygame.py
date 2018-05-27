import pygame # For joystick - python-pygame
import subprocess
import zmq
from time import sleep

class MyZMQ:
    def __init__(self):
        self.disconected = True
        self.enabled = True

        self.zmqPort = 10000

        self.zmqID = "-1"
        zmq_cont = zmq.Context()
        self.publisher = zmq_cont.socket(zmq.PUB)

        def sigINT_Handler(signal, frame):
            print("\nYou pressed Ctrl+C")
            self.publisher.disconnect('tcp://127.0.0.1:'+str(self.zmqPort))
            self.enabled = False
            sleep(0.5)
            sys.exit(0)

        signal.signal(signal.SIGINT, sigINT_Handler)

        self.get_args()
        self.disconnected = not self.connect_zmq()

    def get_args(self):
        if(len(sys.argv) < 2):
            print ("Usage: " + str(sys.argv[0]) + " <ZMQPort> <ID>" )
            sys.exit(0)

        if(len(sys.argv) >= 2):
            self.zmqPort = str(sys.argv[1])

        if(len(sys.argv) >= 3):
            self.zmqID = str(sys.argv[2])

        print("Settings -> ZMQ port: " + self.zmqPort
              + " ID: " + str(self.zmqID))

    def connect_zmq(self):
        try:
            self.publisher.connect('tcp://127.0.0.1:'+str(self.zmqPort))
            sleep(1)
            return True
        except:
            print("Failed to connect to ZMQ, path:")
            print('tcp://127.0.0.1:'+str(self.zmqPort))
            return False

    def send_string(self,data):
        if(not self.disconnected):
            self.publisher.send_string(data)

    def disconnect(self):
        if(not self.disconnected):
            self.disconnected = True
        
import signal   ## for Ctrl+C 
import sys      ## for logger

class MyGamePad:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        self.zMQ = MyZMQ()
        self.zMQ.connect_zmq()
        
        self.my_clock = pygame.time.Clock()
        self.num_of_gamepads = pygame.joystick.get_count()
        
        self.enabled = True
        
        self.enable_serial = False
        
        if(self.num_of_gamepads > 0):
            self.my_gamepad = pygame.joystick.Joystick(0)
            self.my_gamepad.init()
        else:
            print("No gamepad found, exiting...")
            self.enabled = False
            exit(1)

        self.axes_num = self.my_gamepad.get_numaxes()
        self.btns_num = self.my_gamepad.get_numbuttons()
        self.hats_num = self.my_gamepad.get_numhats()

        self.btns_state = []
        for i in range(self.btns_num):
            self.btns_state.append(self.my_gamepad.get_button(i))

        self.hats_state = []
        for i in range(self.hats_num):
            self.hats_state.append(self.my_gamepad.get_hat(i))

        self.axis_state = []
        for i in range(self.axes_num):
            self.axis_state.append(round(self.my_gamepad.get_axis(i),2))
        
        self.main_loop()
        
        self.zMQ.disconnect()
        self.deinit()
        
    def check_buttons_down(self):
        for i in range( self.btns_num):
            if(self.btns_state[i] is not self.my_gamepad.get_button(i)):
                self.zMQ.send_string("gamePad,BTN," + str(i) + ",D,\r\n")
                self.btns_state[i] = self.my_gamepad.get_button(i)

    def check_buttons_up(self):
        for i in range( self.btns_num):
            if(self.btns_state[i] is not self.my_gamepad.get_button(i)):
                self.zMQ.send_string("gamePad,BTN," + str(i) + ",U,\r\n")
                self.btns_state[i] = self.my_gamepad.get_button(i)

    def check_hat(self):
        for i in range(self.hats_num):
            new_hat_state = self.my_gamepad.get_hat(i)
            for j in range(len(self.hats_state[i])): ## 0 = X ; 1 = Y
                if(self.hats_state[i][j] is not new_hat_state[j]):
                    self.zMQ.send_string("gamePad,HAT,"+ str(i) + "," + str(j) + "," +str(new_hat_state[j]) + "\r\n")
                    self.hats_state[i] = new_hat_state
                    
    def check_axes(self):
        # upadate values
        for i in range(self.axes_num):
            new_value = round(self.my_gamepad.get_axis(i),2)
            if(self.axis_state[i] is not new_value):
                self.zMQ.send_string("gamePad,AXS," + str(i) + "," + str(new_value) + "\r\n")
                self.axis_state[i] = new_value
                    
    def main_loop(self):
        while self.enabled:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.enabled = False

                if event.type == pygame.JOYBUTTONDOWN:
                    self.check_buttons_down()
                
                if event.type == pygame.JOYBUTTONUP:
                    self.check_buttons_up()

                if event.type == pygame.JOYHATMOTION:
                    self.check_hat()
            
            self.check_axes();
            
            self.my_clock.tick(10) # omezení na cca 5 Hz

    def deinit(self):
        pygame.quit()
        

logitechFX710 = MyGamePad()
