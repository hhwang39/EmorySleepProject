from __future__ import print_function
from threading import Timer
from time import sleep
from subprocess import call
import sys

counter=0
wdvar=None

class Watchdog:
    def __init__(self, timeout, userHandler=None):  # timeout in seconds
        self.timeout = timeout
        self.handler = userHandler if userHandler is not None else self.defaultHandler
        self.timer = Timer(self.timeout, self.handler)
        self.timer.start()

    def reset(self):
        self.timer.cancel()
        self.timer = Timer(self.timeout, self.handler)
        self.timer.start()

    def stop(self):
        self.timer.cancel()

    def defaultHandler(self):
        raise self

def mywatchdog():
    global counter
    print( "test thread counter ",counter,"seconds")
    counter=counter+1
    wdvar.reset()

timeout=5
wdvar=Watchdog(timeout,mywatchdog)
cycles=100
flagfirstcycle=0
'''while cycles>0:
	print("cycles %d"%cycles)
        sleep(1.0)
        # After 1 cycle, turn Raspberry Pi LED green to indicate successful connection.
        if flagfirstcycle==0:
           call("python testProcess.py &",shell=True) 
           flagfirstcycle=1
        cycles=cycles-1
'''
#retcode=call("python -u testProcess.py ",shell=True,stdout=open("./excep.log","a"))
retcode=call("python -u testProcess.py ",shell=True)
print("exit with code",retcode)
wdvar.stop()
