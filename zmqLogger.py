from Logger import zMQLogger
from time import sleep

A = zMQLogger()
A.addLocalPort("10000")
A.addIP("192.168.0.1:10000") # RaspiCam?

sleep(1)

A.run()
