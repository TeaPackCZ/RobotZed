import pygame # For joystick - python-pygame
import subprocess

class TextPrint:
    def __init__(self):
        size = [500, 700]
        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption("Py Game Debug Window")
        
        self.BLACK  = (   0,   0,   0)
        self.WHITE  = ( 255, 255, 255)
        self.reset()
        self.font = pygame.font.Font(None, 20)

    def my_print(self, textString):
        textBitmap = self.font.render(textString, True, self.WHITE)
        self.screen.blit(textBitmap, [self.x, self.y])
        self.y += self.line_height
        
    def reset(self):
        self.screen.fill(self.BLACK)
        self.x = 10
        self.y = 10
        self.line_height = 15
        
    def indent(self):
        self.x += 10
        
    def unindent(self):
        self.x -= 10

import zmq
from time import sleep

class MyZMQ:
    def __init__(self):
        self.disconected = True
        self.enabled = True

        self.zmqPort = 10501

        self.zmqID = "-1"
        zmq_cont = zmq.Context()
        self.publisher = zmq_cont.socket(zmq.PUB)

        def sigINT_Handler(signal, frame):
            print("\nYou pressed Ctrl+C")
            self.publisher.disconnect('tcp://127.0.0.1:'+str(self.zmqPort))
            self.ser.close()
            self.enabled = False
            self.mfile.flush()
            self.mfile.close()
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

    def send_diff_move(self, value1 = 0.00, value0 = 0.00):
        message = ("$setM,D," + str(int(value0*100))
                    + "," + str(round(value1,2)) + "\r\n")
        if(not self.disconnected):
            self.publisher.send_string(message)

    def send_string(self,data):
        if(not disconnected):
            self.publisher.send_string(data)

    def disconnect(self):
        if(not self.disconnected):
            self.disconnected = True
        
import signal   ## for Ctrl+C 
import sys      ## for logger

class MyGamePad:
    def __init__(self, own_window = False):
        pygame.init()
        pygame.joystick.init()

        self.zMQ = MyZMQ()
        self.zMQ.connect_zmq()
        
        self.my_clock = pygame.time.Clock()
        self.num_of_gamepads = pygame.joystick.get_count()
        
        self.enabled = True
        self.own_window = own_window

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
            self.axis_state.append(self.my_gamepad.get_axis(i))
        
        if(own_window):
            self.textPrint = TextPrint()
            self.textPrint.reset()

        self.hatMap = ["X","Y"]
        self.hatPos = [" ", "+", "-"]
        
        self.main_loop()
        self.zMQ.disconnect()
        self.deinit()
        
    def check_buttons_down(self):
        for i in range( self.btns_num):
            if(self.btns_state[i] is not self.my_gamepad.get_button(i)):
                #print ("Button " + str(i) + " was pressed...")
                if( i == 2 ): ## RED B button
                    self.btn_1_pressed()
                elif( i == 1): ## Green A button
                    self.btn_A_pressed()
                elif( i == 8): ## BACK button
                    self.btn_back_pressed()
                elif( i == 9): ## START button
                    self.btn_start_pressed()
                    
                self.btns_state[i] = self.my_gamepad.get_button(i)

    def check_buttons_up(self):
        for i in range( self.btns_num):
            if(self.btns_state[i] is not self.my_gamepad.get_button(i)):
                #print ("Button " + str(i) + " was released...")
                self.btns_state[i] = self.my_gamepad.get_button(i)

    def check_hat(self):
        for i in range(self.hats_num):
            new_hat_state = self.my_gamepad.get_hat(i)
            for j in range(len(self.hats_state[i])): ## 0 = X ; 1 = Y
                if(self.hats_state[i][j] is not new_hat_state[j]):
                    if(new_hat_state[j] == 0):
                        #print ("Hat was released on Hat_" + str(i)
                        #   + " on axis: " + self.hatMap[j])
                        pass
                    elif(new_hat_state[j] == +1):
                        #print ("Hat was pushed on Hat_" + str(i)
                        #   + " on axis: " + self.hatPos[new_hat_state[j]] + self.hatMap[j])
                        pass
                    elif(new_hat_state[j] == -1):
                        #print ("Hat was pushed on Hat_" + str(i)
                        #   + " on axis: " + self.hatPos[new_hat_state[j]] + self.hatMap[j])
                        pass
                    self.hats_state[i] = new_hat_state
                    
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

            axes = self.my_gamepad.get_numaxes()
            if(self.own_window):
                self.textPrint.reset()
                #self.textPrint.my_print("Number of axes: {}".format(axes) )
                self.textPrint.indent()

            for i in range(self.axes_num):
                self.axis_state[i] = self.my_gamepad.get_axis(i)

            self.zMQ.send_diff_move(-self.axis_state[1], -self.axis_state[3])

            if(self.own_window):
                for i in range( self.axes_num ):
                    axis = self.my_gamepad.get_axis( i )
                    #self.textPrint.my_print("Axis {} value: {:>6.3f}".format(i, axis) )
                pygame.display.flip()
            
            self.my_clock.tick(10) # omezení na 5Hz

    def deinit(self):
        pygame.quit ()

    ## BUTTONS EVENTS - to be transmitted via ZMQ

    def btn_1_pressed(self):
        print ("Stop robot ... ")
        self.zMQ.send_string("$setD,M,0,0\r\n")

    def btn_A_pressed(self):
        print ("Start ZMQ")
        #subprocess.call("./zmq_init.sh")

    def btn_back_pressed(self):
        print ("EXIT ... ")
        self.zMQ.send_string("$setD,T,0,0,\r\n")
        self.enabled = False

    def btn_start_pressed(self):
        print ("Enable robot ... ")
        self.zMQ.send_string("$setD,M,1,1\r\n")

logitechFX710 = MyGamePad()
