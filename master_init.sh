#!/bin/bash

python zmqLogger.py &

python main.py &
python gpsNavStarter.py &

#python gpsReader.py /dev/ttyS3 115200 10101 GPS1 &
#python gpsReader.py /dev/ttyS4 115200 10102 GPS2 &

python gpsReader.py Logs/log_GPS1_15_45_36 115200 10101 GPS1 &
python gpsReader.py Logs/log_GPS2_15_45_36 115200 10102 GPS2 &

exit 0
