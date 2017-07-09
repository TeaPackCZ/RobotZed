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


if __name__ == '__main__':
    unittest.main()
