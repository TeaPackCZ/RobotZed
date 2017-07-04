from Logger import zMQLogger
from time import sleep

A = zMQLogger()
A.addLocalPort("10101") # GPS1
A.addLocalPort("10102") # GPS2
A.addLocalPort("10111") # GPSNav
A.addLocalPort("10301") # test1
A.addLocalPort("10302") # test2
A.addIP("192.168.0.1:9000") # RaspiCam?

sleep(1)

A.run()
