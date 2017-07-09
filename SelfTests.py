import os
import unittest
from Logger import Logger

class TestLogger(unittest.TestCase):
    def test_file_handling(self):
        testLog = Logger("testLog")
        ## Check if program can create and open file
        self.assertTrue(testLog.opened)
        returns = testLog.close()
        ## Check if logger correctly signs bool OPENED and returns
        ##     0 as succes.
        self.assertFalse(testLog.opened)
        self.assertEqual(returns,0)
        returns = testLog.close()
        ## Check if logger returns 1 when trying to close already
        ##     closed file
        self.assertEqual(returns,1)
        ## Do cleanup:
        os.remove(testLog.name)
        
    def test_logging(self):
        testLog = Logger("testLog")
        testPhrase = "TestLine\r\n"
        testLog.save_line(testPhrase)
        testLog.close()
        logfile = open(testLog.name)
        content = logfile.read()
        logfile.close()
        saved = content.split(" : ")
        ## Check if saved data corresponds
        self.assertEqual(saved[1],testPhrase)
        ## cleanup
        os.remove(testLog.name)

from gpsNavigation import gpsModule,gpsPoint
class TestGPSNavigation(unittest.TestCase):
    def test_gps_angles(self):
        gpsMod = gpsModule()

        A = gpsPoint(10,10)
        B = gpsPoint(10.1,10.1)
        
        distance, azimut = gpsMod.GPSData.getDirAndDist(A,B)
        self.assertEqual(distance,15623.0)
        self.assertEqual(azimut,45.0)

        B = gpsPoint(10.0,10.1)
        distance, azimut = gpsMod.GPSData.getDirAndDist(A,B)
        self.assertEqual(distance,10963.0)
        self.assertEqual(azimut,90.0)

        B = gpsPoint(9.9,10.1)
        distance, azimut = gpsMod.GPSData.getDirAndDist(A,B)
        self.assertEqual(distance,15625.0)
        self.assertEqual(azimut,135.0)

        B = gpsPoint(9.9,10.0)
        distance, azimut = gpsMod.GPSData.getDirAndDist(A,B)
        self.assertEqual(distance,11132.0)
        self.assertEqual(azimut,180.0)

        B = gpsPoint(9.9,9.9)
        distance, azimut = gpsMod.GPSData.getDirAndDist(A,B)
        self.assertEqual(distance,15625.0)
        self.assertEqual(azimut,225.0)

        B = gpsPoint(10.0,9.9)
        distance, azimut = gpsMod.GPSData.getDirAndDist(A,B)
        self.assertEqual(distance,10963.0)
        self.assertEqual(azimut,270.0)

        B = gpsPoint(10.1,9.9)
        distance, azimut = gpsMod.GPSData.getDirAndDist(A,B)
        self.assertEqual(distance,15623.0)
        self.assertEqual(azimut,315.0)

        B = gpsPoint(10.1,10.0)
        distance, azimut = gpsMod.GPSData.getDirAndDist(A,B)
        self.assertEqual(distance,11132.0)
        self.assertEqual(azimut,0)


if __name__ == '__main__':
    unittest.main()
