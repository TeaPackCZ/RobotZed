#!/bin/bash

python zmqLogger.py &

sleep 1

python main.py &
#python gpsNavStarter.py &

python mbed.py /dev/ttyS2 115200 10201 mbed &

#python gpsReader.py /dev/ttyS3 115200 10101 GPS1 &
#python gpsReader.py /dev/ttyS4 115200 10102 GPS2 &

python gamepad_pygame.py 10501 FX710 &

#python gpsReader.py Logs/log_GPS1_15_45_36 115200 10101 GPS1 &
#python gpsReader.py Logs/log_GPS2_15_45_36 115200 10102 GPS2 &

exit 0
