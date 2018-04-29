import pandas as pd
import time
import logging
from datetime import datetime
from threading import Timer
import sqlite3
import numpy as np
from time import sleep
import RPi.GPIO as GPIO
import sys

#import logging
#logging.basicConfig(level=logging.DEBUG)
#logger = logging.getLogger(__name__)

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



class Calibration:
    def __init__(self,address):

            
        self.address=address
        val3s=pd.Timedelta(3, unit='s')

        self.offset=0
        self.conn = self.getConnection()

        print("In Process of Reading data")
        t = time.time()
        
        query="SELECT * from acc limit 100000 offset {off} ;".\
            format(off=self.offset)
        
        print("query: %s",query)
        df = pd.read_sql_query(query, self.conn)
        
        print("register read: %s",len(df['epoch']))
        self.offset=len(df['epoch'])
        
        elapsed = time.time() - t
        print("time taken to read query is {:f}".format(elapsed))
        self.conn.close()

        t = time.time()

        df['epoch']=pd.to_datetime(df['epoch'], unit='ms')
        df['epoch']=df['epoch'].dt.tz_localize('UTC').dt.tz_convert('America/New_York')
        
        self.df = df
        elapsed = time.time() - t
        print("time taken to process data {:f}".format(elapsed))
        
        print(df.head())
        print("datetime of first record %s",df.iloc[0,0])

        startDate=df.iloc[0,0]

        self.valueCal=["valuez","valuez","valuey","valuey","valuex","valuex"]
        
        self.calIndex=0

        self.valsMax=[0.0,0.0,0.0,0.0,0.0,0.0]
        self.valsCal=[0.0,0.0,0.0,0.0,0.0,0.0]


        timeout=0.5
        self.wdvar=Watchdog(timeout,self.updateData)
        self.wdvar.stop()
        self.datacapture=False


    def updateData(self):
        self.conn = self.getConnection()
        query="SELECT * from acc limit 100000 offset {off} ;".\
            format(off=self.offset)
        df = pd.read_sql_query(query, self.conn)

        self.offset=self.offset+len(df['epoch'])
        
        if len(df['epoch'])>0:
            df['epoch']=pd.to_datetime(df['epoch'], unit='ms')
            df['epoch']=df['epoch'].dt.tz_localize('UTC').dt.tz_convert('America/New_York')
            self.df=self.df.append(df)

        if self.datacapture:
            self.wdvar.reset()



    def getConnection(self):
        """
        get the connection of sqlite given file name
        :param filename:
        :return: sqlite3 connection
        """
        conn = sqlite3.connect('data1.db', check_same_thread=False)
        return conn

    def startCalibration(self):
        self.datacapture=True
        self.wdvar.reset()
        
    def stopCalibration(self):
        self.wdvar.stop()
        self.datacapture=False

        val3s=pd.Timedelta(3, unit='s')

        vepochStop=self.df['epoch']
        datevaluesStop= vepochStop.dt.to_pydatetime()
        endDate=datevaluesStop[-1]
        startDate=endDate-val3s

        mask=(datevaluesStop >= startDate) & (datevaluesStop <= endDate)
        avg=np.average(self.df.loc[mask, self.valueCal[self.calIndex]])
        self.valsMax[self.calIndex]=avg

        if (self.calIndex+1) % 2 ==0:
            #Calculate Offset
            self.valsCal[self.calIndex-1]=0.5*(self.valsMax[self.calIndex-1]+self.valsMax[self.calIndex])
            #Calculate Gain
            self.valsCal[self.calIndex]=0.5*(self.valsMax[self.calIndex-1]-self.valsMax[self.calIndex])
        print(self.df[self.valueCal[self.calIndex]].iloc[-6:-1])

        self.calIndex=self.calIndex+1

    def finishCalibration(self):
        rows=['ZOffset','ZGain','YOffset','YGain','XOffset','XGain']

        d = {'Titles': rows, 'Values': self.valsCal}
        index = ['Row'+str(i) for i in range(1, len(self.valsCal)+1)]
        df = pd.DataFrame(data=d, index=index)

        fileName='calibrationResults'+self.address+'.csv'
        df.to_csv(fileName, sep=",", encoding='utf-8')
        

    def setupGPIOLED(self):
        # Setting GPIO Mode to use BCM pin numbers
        GPIO.setmode(GPIO.BCM)
	# Disable warnings for GPIO pins
        GPIO.setwarnings(False)
	# Initialize red, green, and blue LED pins 
        self.redLED=23
        self.greenLED=22
        self.blueLED=24
        channels=[self.redLED,self.greenLED, self.blueLED]
	# Set green and blue led to output pins.
        GPIO.setup(channels,GPIO.OUT)

    def turnOffLEDs(self):
        GPIO.output(self.redLED, GPIO.LOW)
        GPIO.output(self.greenLED, GPIO.LOW)
        GPIO.output(self.blueLED, GPIO.LOW)
        print("Turning Off LEDs")
        
    def turnOnMagenta(self):
        self.turnOffLEDs()
        GPIO.output(self.redLED, GPIO.HIGH)
        GPIO.output(self.blueLED, GPIO.HIGH)
        print("Turning On Magenta")
    def turnOnCyan(self):
        self.turnOffLEDs()
        GPIO.output(self.blueLED, GPIO.HIGH)
        GPIO.output(self.greenLED, GPIO.HIGH)
        print("Turning On Cyan")
    def turnOnYellow(self):
        self.turnOffLEDs()
        GPIO.output(self.redLED, GPIO.HIGH)
        GPIO.output(self.greenLED, GPIO.HIGH)
        print("Turning On Yellow")
    def turnOnWhite(self):
        self.turnOffLEDs()
        GPIO.output(self.redLED, GPIO.HIGH)
        GPIO.output(self.greenLED, GPIO.HIGH)
        GPIO.output(self.blueLED, GPIO.HIGH)
        print("Turning On White")
    def turnOnRed(self):
        self.turnOffLEDs()
        GPIO.output(self.redLED, GPIO.HIGH)
        print("Turning On Red")
    def turnOnBlue(self):
        self.turnOffLEDs()
        GPIO.output(self.blueLED, GPIO.HIGH)
        print("Turning On Blue")
    def turnOnGreen(self):
        self.turnOffLEDs()
        GPIO.output(self.greenLED, GPIO.HIGH)
        print("Turning On Green")

    

        
            

address=sys.argv[1]
print("Starting Calibration")

calibObj = Calibration(address)

# Calibration of Positive Z-Axis
calibObj.setupGPIOLED()
calibObj.startCalibration()
calibObj.turnOnMagenta()

sleep(30.0)
calibObj.stopCalibration()

# Calibration of Negative Z-Axis
calibObj.startCalibration()
calibObj.turnOnCyan()

sleep(15.0)
calibObj.stopCalibration()

# Calibration of Positive Y-Axis
calibObj.startCalibration()
calibObj.turnOnYellow()

sleep(15.0)
calibObj.stopCalibration()

# Calibration of Negative Y-Axis
calibObj.startCalibration()
calibObj.turnOnWhite()

sleep(15.0)
calibObj.stopCalibration()

# Calibration of Positive X-Axis
calibObj.startCalibration()
calibObj.turnOnRed()

sleep(15.0)
calibObj.stopCalibration()

# Calibration of Negative X-Axis
calibObj.startCalibration()
calibObj.turnOnBlue()

sleep(15.0)
calibObj.stopCalibration()

calibObj.turnOnWhite()

calibObj.finishCalibration()
sleep(3.0)
calibObj.turnOffLEDs()






