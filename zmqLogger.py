from Logger import zMQLogger
from time import sleep

A = zMQLogger()
A.addLocalPort("10101") # GPS1
A.addLocalPort("10102") # GPS2
A.addLocalPort("10111") # GPSNav->Main

A.addLocalPort("10201") # Main->GPSNav & GPS1 & GPS2
A.addLocalPort("10202") # test2

A.addLocalPort("10300") # Main->Mbed
A.addLocalPort("10302") # Mbed->Main

A.addIP("192.168.0.1:9000") # RaspiCam?

sleep(1)

A.run()
