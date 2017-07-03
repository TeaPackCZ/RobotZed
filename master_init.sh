#!/bin/bash

python zmqLogger.py &

#python gpsReader.py /dev/ttyS3 38400 10101 GPS1 &
python gpsReader.py Logs/log_GPS1_15_45_36 38400 10101 GPS1 &
python gpsReader.py Logs/log_GPS2_15_45_36 38400 10102 GPS2 &

exit 0
