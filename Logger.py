import time

class Logger():
    def __init__(self, name = "defaultLogFile"):
        timestamp = time.strftime('%Y_%m_%d-%H_%M_%S')
        self.name = "Logs/" + timestamp + "_" + name + ".txt"
        try:
            self.logfile = open(self.name, 'w')
            self.opened = True
        except:
            self.opened = False

    def save_line(self,data):
        time_s = time.time()
        time_ms = int(round((time_s - round(time_s))*1000))
        timestamp = time.strftime(('%H_%M_%S'), time.localtime(time_s))+"_" +str(time_ms) + " : "
        if(self.opened):
            self.logfile.write(timestamp+data)
            self.logfile.flush()
            return 0,""
        else:
            return 1,str(timestamp+data)

    def close(self):
        if(self.opened):
            self.logfile.flush()
            self.logfile.close()
            self.opened = False
            return 0
        else:
            return 1
            