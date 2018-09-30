from Logger import zMQLogger
from time import sleep

A = zMQLogger()
A.addLocalPort("10101") # GPS1->GPSNav
A.addLocalPort("10102") # GPS2->GPSNav
A.addLocalPort("10105") # GPSNav->Main
A.addLocalPort("10110") # Main->GPSNav & GPS1 & GPS2 

A.addLocalPort("10201") # Mbed->Main
A.addLocalPort("10210") # Main->Mbed

#A.addIP("192.168.0.1:9000") # RaspiCam?

sleep(1)

A.run()
