import sqlite3
import pandas as pd
#import matplotlib.pyplot as plt
import numpy as np
import time
# from matplotlib.widgets import SpanSelector
# import matplotlib.patches as matpat
from matplotlib.patches import Rectangle
import random
import matplotlib.dates as mdates
from matplotlib.widgets import RadioButtons, CheckButtons
from matplotlib.widgets import Cursor
from matplotlib.ticker import LinearLocator
import matplotlib as mpl
import os
import re
import threading

PRE_DEF_CLICK_TIME = 0.5

#Added Eastern TimeZone
mpl.rcParams['timezone'] = 'US/Eastern'

class myThread(threading.Thread):
    def __init__(self,threadID,name,parent):
        threading.Thread.__init__(self)
        self.threadID=threadID
        self.name=name
        self.parent=parent
    def run(self):
        print("Starting "+self.name)
        self.graphsingle()
        print("Exiting "+self.name)
        
    def graphsingle(self):
        if self.name=="mag":
            self.parent.lm,  = self.parent.ax2.plot(self.parent.df["epoch"].iloc[0:3], self.parent.df["mag"].iloc[0:3],'C0-',visible=True)
            self.parent.lm.set_data(self.parent.datevalues, self.parent.df["mag"])
            #self.parent.lm,  = self.parent.ax2.plot(self.parent.df["epoch"], self.parent.df["mag"],visible=True)
        elif self.name=="valuex":
            print("plotting valuex")
            self.parent.lx,  = self.parent.ax2.plot(self.parent.df["epoch"].iloc[0:3], self.parent.df["valuex"].iloc[0:3],'C1-',visible=True)
            self.parent.lx.set_data(self.parent.datevalues, self.parent.df["valuex"])
            #self.parent.lx,  = self.parent.ax2.plot(self.parent.df["epoch"], self.parent.df["valuex"],visible=False)
        elif self.name=="valuey":
            print("plotting valuey")
            self.parent.ly,  = self.parent.ax2.plot(self.parent.df["epoch"].iloc[0:3], self.parent.df["valuex"].iloc[0:3],'C2-',visible=True)
            self.parent.ly.set_data(self.parent.datevalues, self.parent.df["valuey"])
            #self.parent.ly,  = self.parent.ax2.plot(self.parent.df["epoch"], self.parent.df["valuey"],visible=False)
        elif self.name=="valuez":
            print("plotting valuez")
            self.parent.lz,  = self.parent.ax2.plot(self.parent.df["epoch"].iloc[0:3], self.parent.df["valuex"].iloc[0:3],'C3-',visible=True)
            self.parent.lz.set_data(self.parent.datevalues, self.parent.df["valuez"])

class ECERectangle(Rectangle):
    def __init__(self, x, y, width, height,
                 color, index):
        Rectangle.__init__(self, (x, y), width, height, fill=True,
                           alpha=0.4, color=color, picker=True)
        self.next = None
        self.index = index
    def setNext(self, rect):
        self.next = rect
    def setPrev(self, rect):
        self.prev = rect
    def getNext(self):
        return self.next
    def getPrev(self):
        return self.prev
    def getIndex(self):
        return self.index


class ECE4012:
    def __init__(self, figure, filename, toolbar):
        self.dfCal = None
        self.fig = figure
        self.toolbar = toolbar
        self.filename=filename
        self.rect = None
    def initializer(self,type):
        self.fig.clear()
        print("celar figure")
        self.fig.subplots_adjust(hspace=1.0)       
        self.annoteText = "annotated"
        #self.fig = figure
        #self.toolbar = toolbar
        self.isAnnotate = False
        self.fig.canvas.mpl_connect('button_release_event', self.onrelease)
        self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.fig.canvas.mpl_connect('key_press_event', self.onpress)
        self.fig.canvas.mpl_connect('pick_event', self.onpick)
        # print(self.fig)
        if type == "DB":
            self.searchOpenCalibration(self.filename)
            self.conn = self.getConnection(self.filename)
        # df = pd.read_sql_query("select * from  acc LIMIT 100000;", self.conn)
            t = time.time()
            df = pd.read_sql_query("select * from  acc;", self.conn)
            elapsed = time.time() - t
            print("time taken to read data was {:f}".format(elapsed))
        elif type == "CSV":
            print("CSV getting Calibration")
            self.searchOpenCalibration(self.filename)
            print("CSV opening file")
            df= pd.read_csv(self.filename)
            print("CSV opened file")


        print("Starting")
        
        if self.dfCal is not None:
            df["valuex"] = np.subtract(df["valuex"],self.dfCal['Values'][self.XOffset])/self.dfCal['Values'][self.XGain]
            df["valuey"] = np.subtract(df["valuey"], self.dfCal['Values'][self.YOffset])/self.dfCal['Values'][self.YGain]
            df["valuez"] = np.subtract(df["valuez"], self.dfCal['Values'][self.ZOffset])/self.dfCal['Values'][self.ZGain]        

        # DONE !!TODO this calibartion should change to either actual calibration from
        # metawear C
        # print(len(df["valuex"]))
        # avgX = np.sum(df["valuex"]) / len(df["valuex"])
        # avgY = np.sum(df["valuey"]) / len(df["valuey"])
        # avgZ = np.sum(df["valuez"]) / len(df["valuez"])
        # df["valuex"] = np.subtract(df["valuex"], avgX)
        # df["valuey"] = np.subtract(df["valuey"], avgY)
        # df["valuez"] = np.subtract(df["valuez"], avgZ)
        #self.axTop = self.fig.add_subplot(2, 1, 1)
        #self.axBottom = self.fig.add_subplot(2, 1, 2)
        self.fig.subplots_adjust(bottom=0.3,left=0.2,hspace=1.0)
        self.labels=['30 sec','5 min','30 min', '1 hr', '2 hr']
        sec30 = pd.Timedelta(30, unit='s')
        min5 = pd.Timedelta(5, unit='m')
        min30 = pd.Timedelta(30, unit='m')
        hr1 =pd.Timedelta(1, unit='h')
        hr2 =pd.Timedelta(2, unit='h')

        # Scale Radio Buttons for Zoom
        self.scaleDeltaArray=[sec30, min5, min30, hr1, hr2]
        self.rax = self.fig.add_axes([0.02, 0.7, 0.11, 0.15])
        self.rax.set_title('Scale')
        self.check = RadioButtons(self.rax, self.labels)
        self.fig.canvas.mpl_connect('button_press_event', self.onclick)

        # Data Set Selection Check Box
        self.rcbax = self.fig.add_axes([0.02, 0.25, 0.11, 0.15])
        self.rcbax.set_title('DataSet')
        self.checkBox = CheckButtons(self.rcbax, ('valuex', 'valuey', 'valuez','mag'), (True, True, True,True))
        self.checkBox.on_clicked(self.oncheck)
        xs = np.linspace(15,21,200)
        horiz_line_dataz = np.array([0.41 for i in range(len(xs))])
        self.rcbax.plot(xs, horiz_line_dataz, 'C3-')
        horiz_line_datam = np.array([0.26 for i in range(len(xs))])
        self.rcbax.plot(xs, horiz_line_datam, 'C0-')
        horiz_line_datay = np.array([0.58 for i in range(len(xs))])
        self.rcbax.plot(xs, horiz_line_datay, 'C2-')
        horiz_line_datax = np.array([0.73 for i in range(len(xs))])
        self.rcbax.plot(xs, horiz_line_datax, 'C1-') 

        
        self.check.on_clicked(self.changeScale)
        df["mag"] = np.sqrt(np.square(df["valuex"]) + np.square(df['valuey']) + \
                            np.square(df["valuez"]))-1.0
        print("Normalize")
        ya_min = df.loc[:, "mag"].min() - 0.1
        ya_max = df.loc[:, "mag"].max() + 0.1
        print("y limit (max={:f},min={:f})".format(ya_max,ya_min))
        # print("Normalized")
        # print(type(ya_min))
        # print(ya_max)

        # print(df["mag"])
        # df["mag"] = df["mag"] - 1 # subtract 1g
        
        
        #Convert epoch to datetime to see the right value
        print("Convert Date Time")
        print(df["epoch"].iloc[0])
        print(df["epoch"].iloc[1])
        if type == "DB":
            print("epoch type",df.dtypes[0])
            df['epoch'] = pd.to_datetime(df['epoch'], unit='ms')
        elif type == "CSV":
            print("epoch type",df.dtypes[0])
            if 'annotated' not in df.columns:
                df['epoch'] = pd.to_datetime(df['epoch'], unit='ms')
            else:
                df['epoch'] = pd.to_datetime(df['epoch'])       
        print("epoch type after",df.dtypes[0])
        
        # Adjusting epoch time to be on Eastern Time Zone 
        df['epoch']=df['epoch'].dt.tz_localize('UTC').dt.tz_convert('America/New_York')
        vepoch=df['epoch']
        self.datevalues= vepoch.dt.to_pydatetime()


        if 'annotated' not in df.columns:
            charArr = np.chararray((len(df["mag"], )), unicode=True)
            charArr[:] = ' '
            df["annotated"] = pd.DataFrame(charArr)
            df["colorHex"] = pd.DataFrame(charArr)

        # print(df["epoch"])
        # print(type(df['epoch'][0]))
        #Definition of x-axis formatter of tick
        # self.hoursFmt = mdates.DateFormatter('%Y-%m-%d %H:%M:%S') #Week Month/Day H:M:S
        self.hoursFmt = mdates.DateFormatter('%a-%m-%d %H:%M:%S')
        self.HMSFmt = mdates.DateFormatter('%H:%M:%S')
        #Get total time of the data in hours
        startDate = df["epoch"].iloc[0]
        self.startDate=startDate
        endDate = df["epoch"].iloc[-1]
        totaltime = int(endDate.timestamp() * 1000) - \
                    int(startDate.timestamp() * 1000)
        total_hours = totaltime/1000/3600 #totaltime in hours
        total_minutes=total_hours*60
        print("total hours {:f}".format(total_hours))

        #create variable to track drag time
        self.timeTrack=0
        #create variable to track initial click xpos
        self.xpos = 0
        self.df = df

        print("Creating Top Graph")
        
        self.ax = self.fig.add_subplot(2, 1, 1)
        # second axis
        print("Creating Bottom Graph")
        self.ax2 = self.fig.add_subplot(2, 1, 2)
        #adjust distance between toolbar and graph to give more space
        self.fig.subplots_adjust(bottom=0.145)

        #adjust distance between toolbar and graph if data is 24 hours or more
        if total_hours > 24:
            self.fig.subplots_adjust(hspace=1.3)
        print("Start Plot Setting")
        
        # Set default values for x aixs
        ##changed temporary pls ignore
        # self.ax.set_ylim(1, 1.1)
        # self.ax2.set_ylim(1, 1.1)
        #self.ax.set_ylim(0, 8)
        #self.ax2.set_ylim(0, 8)
        self.ax.set_xlabel("Time (H:M:S)")
        self.ax2.set_xlabel("Time (H:M:S)")
        self.ax.set_ylabel("Acceleration (g)")
        self.ax2.set_ylabel("Acceleration (g)")
        #self.ax.set_title('Scale')
        self.ax.set_ylim(ya_min, ya_max)
        self.ax2.set_ylim(ya_min, ya_max)
        bottomtitle='Magnitude Graph for Start Date '+"{:%Y-%m-%d}".format(startDate)
        if self.dfCal is not None:
            bottomtitle='Calibrated '+bottomtitle
        self.ax.set_title(bottomtitle)

        toptitle='Zoomed-In Graph for Start Date '+"{:%Y-%m-%d}".format(startDate)
        if self.dfCal is not None:
            toptitle='Calibrated '+toptitle
        self.ax2.set_title(toptitle)
        
        # self.ya_min = ya_min
        # self.ya_max = ya_max
        # start date
        # print(type(df["epoch"]))
        # print(len(df["epoch"]))
        # print(df["epoch"])
        # print()
        # TODO we assume time is not empty but it could be good to chek empty
        start_time = df["epoch"].iloc[0]
        print("start time={v}".format(v=start_time))
        # print(type(start_time))
        if total_hours>1:
            end_time = start_time + hr1
        elif total_minutes>30:
            end_time = start_time + min30
        elif total_minutes>5:
            end_time = start_time + min5
        else:
            end_time = start_time + sec30
        print("end time={v}".format(v=end_time))
        # print(type(start_time))
        #end_time = start_time + pd.Timedelta(hours=1)
        #print(end_time)
        self.startX = start_time
        self.endX = end_time
        
        # set axis 2
        self.ax2.set_xlim(start_time, end_time)
        print("Set Limit")
        # print(type(df["epoch"].iloc[0]))
        mask = (df["epoch"] >= start_time) & (df["epoch"] <= end_time)
        print("Plotting")
        # print(mask)
        # print(df.loc[mask, "epoch"])
        # plot
        t = time.time()
        self.plotTop,  = self.ax.plot(df["epoch"].iloc[0:3], df["mag"].iloc[0:3],visible=True)
        self.plotTop.set_data(self.datevalues, df["mag"])
        self.ax.relim()
        self.ax.autoscale_view(True,True,True)
        self.fig.canvas.draw()
        
        #self.ax.plot(df["epoch"], df["mag"])
        elapsed = time.time() - t
        print("time taken to top graph magnitud was {:f}".format(elapsed))
        # print(df.loc[mask, "epoch"])
        print(len(df.loc[mask, "epoch"]))
        t = time.time()
        self.lm,  = self.ax2.plot(df["epoch"].iloc[0:3], df["mag"].iloc[0:3],visible=True)
        self.lm.set_data(self.datevalues, df["mag"])
        self.ax2.relim()
        self.ax2.autoscale_view(True,True,True)
        self.fig.canvas.draw()
        #self.lm,  = self.ax2.plot(df["epoch"], df["mag"],visible=True)
        elapsed = time.time() - t
        print("time taken to bottom graph magnitud was {:f}".format(elapsed))
        t = time.time()
        try:
            thread1=myThread(1,"valuex",self)
            thread1.start()
        except:
           print("Error: unable to start thread")
        #self.lx,  = self.ax2.plot(df["epoch"], df["valuex"],visible=False)
        elapsed = time.time() - t
        print("time taken to bottom graph valuex was {:f}".format(elapsed))
        t = time.time()
        try:
            thread2=myThread(2,"valuey",self)
            thread2.start()
        except:
           print("Error: unable to start thread")
        #self.ly,  = self.ax2.plot(df["epoch"], df["valuey"],visible=False)
        elapsed = time.time() - t
        print("time taken to bottom graph valuey was {:f}".format(elapsed))
        t = time.time()
        try:
            thread3=myThread(3,"valuez",self)
            thread3.start()
        except:
           print("Error: unable to start thread")
        #self.lz,  = self.ax2.plot(df["epoch"], df["valuez"],visible=False)
        elapsed = time.time() - t
        print("time taken to bottom graph valuez was {:f}".format(elapsed))
        # x in the range
        tX = df.loc[mask, "epoch"]
        self.ax2.set_xlim(tX.iloc[0], tX.iloc[len(tX) - 1])
        # self.ax.xaxis.set_major_formatter(self.hoursFmt)
        self.ax.xaxis.set_major_formatter(self.HMSFmt)
        self.ax.get_xaxis().set_major_locator(LinearLocator(numticks=12))
        #setup format of ticks to Weekday month/day if data is 24 hours or more
        if total_hours>24:
            self.ax.xaxis.set_major_formatter(self.hoursFmt)



        #Rotate labels on x-axis 45 degrees and set font size to 8
        self.ax.tick_params(axis='x', labelsize=8, rotation=45)
        # self.ax.title("Magnitude")
        # self.ax2.plot(df["epoch"], df["valuex"],
        #               color=self.colorChoose(255, 0, 255))
        # self.ax2.plot(df["epoch"], df["valuey"],
        #               color=self.colorChoose(255, 0, 0))
        # self.ax2.plot(df["epoch"], df["valuez"],
        #               color=self.colorChoose(255, 255, 0))
        self.color = self.colorChoose(random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255))
        self.removedObj = None
        # self.ax.add_patch(rect)
        self.fig.canvas.draw()
        self.fig.canvas.mpl_connect('motion_notify_event', self.onmouseover)
        self.cursor = Cursor(self.ax, useblit=True, horizOn=False, color='red', linewidth=2)
        self.cursor.connect_event('button_press_event', self.cursorOnclick)
        self.currentDelta= pd.Timedelta(30, unit='s')
        self.ax2.xaxis.set_major_formatter(self.HMSFmt)
        self.ax2.get_xaxis().set_major_locator(LinearLocator(numticks=7))

        #data text axes
        #self.txtax = self.fig.add_axes([0.75, 0.85, 0.11, 0.05])
        #self.txtax.axis('off')

        self.ax.format_coord = self.format_coord
        if type == "CSV" and 'annotated' in df.columns:
            print("calling searchForAnnotation")
            self.searchForAnnotation()

        

        #self.txt = self.ax.text(0.8, 1.05, 'X,Y,Z Values', transform=self.ax.transAxes)
        #self.txt = self.txtax.text(0.05, 0.05, 'X,Y,Z Values', transform=self.txtax.transAxes)
    
    def format_coord(self,x,y):
        dateclickOn=mdates.num2date(x)
        idx=self.df['epoch'].searchsorted(dateclickOn)
        idx=idx-1
            #logger.debug("dateclickOn:%s idx=%s", dateclickOn,idx)
        vx=self.df['valuex'].values[idx][0]
        vy=self.df['valuey'].values[idx][0]
        vz=self.df['valuez'].values[idx][0]
        vm=self.df['mag'].values[idx][0]
        #print("d: {:%H:%M:%S} vx:{:1.5f} vy:{:1.5f} vz:{:1.5f}".format(dateclickOn,vx,vy,vz))
        #self.txt.set_text('%H:%M:%S x=%1.3f, y=%1.3f, z=%1.3f' % (dateclickOn,vx, vy,vz))
        return "{:%H:%M:%S} M:{:1.3f}".format(dateclickOn,vm)

    def readCalibration(self,filename):
        self.dfCal = pd.read_csv(filename)
        print('Results: %s', self.dfCal)
        print('title: %s', self.dfCal['Titles'])
        print('values: %s', self.dfCal['Values'])
        print('ZGain: %s', self.dfCal['Values'][1])
        self.ZOffset=0
        self.ZGain=1
        self.YOffset=2
        self.YGain=3
        self.XOffset=4
        self.XGain=5

    
    def redrawAfterCalibrate(self):

        print("Computing new data")

        if self.dfCal is not None:
            self.df["valuex"] = np.subtract(self.df["valuex"],self.dfCal['Values'][self.XOffset])/self.dfCal['Values'][self.XGain]
            self.df["valuey"] = np.subtract(self.df["valuey"], self.dfCal['Values'][self.YOffset])/self.dfCal['Values'][self.YGain]
            self.df["valuez"] = np.subtract(self.df["valuez"], self.dfCal['Values'][self.ZOffset])/self.dfCal['Values'][self.ZGain]        
        print("Computing new mag")

        self.df["mag"] = np.sqrt(np.square(self.df["valuex"]) + np.square(self.df['valuey']) + \
                            np.square(self.df["valuez"]))-1.0
        print("setting titles")
        bottomtitle='Magnitude Graph for Start Date '+"{:%Y-%m-%d}".format(self.startDate)
        if self.dfCal is not None:
            bottomtitle='Calibrated '+bottomtitle
        self.ax.set_title(bottomtitle)

        toptitle='Zoomed-In Graph for Start Date '+"{:%Y-%m-%d}".format(self.startDate)
        if self.dfCal is not None:
            toptitle='Calibrated '+toptitle
        self.ax2.set_title(toptitle)

        print("redraw graph")

        self.plotTop.set_ydata(self.df["mag"])
        self.lm.set_ydata(self.df["mag"])
        self.lx.set_ydata(self.df["valuex"])
        self.ly.set_ydata(self.df["valuey"])
        self.lz.set_ydata(self.df["valuez"])
        self.fig.canvas.draw()




    
    def onmouseover(self,event):

        if event.inaxes == self.rax:
            None
            #logger.debug("click on radiobutton")
            #self.check._clicked(event)
        if event.inaxes == self.ax:
            self.cursor.onmove(event)

    def searchOpenCalibration(self,filename):
        directory=os.path.dirname(filename)
        print("directory="+directory)
        tosearch=re.compile('^calibrationResults.*')
        for sChild in os.listdir(directory):
            print("file="+sChild)
            if tosearch.match(sChild) is not None:
                if directory == "":
                    directory="."
                calibfilename=directory+"/"+sChild
                print("calibfilename="+calibfilename)
                self.readCalibration(calibfilename)
                break
    def searchForAnnotation(self):
        colorKick = self.colorChoose(255, 0, 0)
        colorSleep = self.colorChoose(0, 0, 255)
        colorRandom = self.colorChoose(0, 255, 0)
        randomColor = self.color
        
        maskKick= self.df['annotated']=="Kick"
        maskSleep= self.df['annotated']=="Sleep"
        maskRandom= self.df['annotated']=="Random"
        maskColorRandom = self.df['annotated']=="annotated"

        print("masked found")

        if len(self.df.loc[maskKick,'epoch'])>0:
            self.reDrawAnnotation(maskKick,colorKick)
        if len(self.df.loc[maskSleep,'epoch'])>0:
            self.reDrawAnnotation(maskSleep,colorSleep)
        if len(self.df.loc[maskRandom,'epoch'])>0:
            self.reDrawAnnotation(maskRandom,colorRandom)
        if len(self.df.loc[maskColorRandom,'epoch'])>0:
            self.reDrawAnnotation(maskColorRandom,randomColor)
            
    def reDrawAnnotation(self,mask,color):
        
        [ymin, ymax] = self.ax.get_ylim()
        height = ymax - ymin
        
        positionKick=np.array(self.df.index[mask].tolist())
      
        diff=np.subtract(positionKick[1:-1],positionKick[0:-2])
        
        maskcuts=diff>1
        posInCuts=np.where(maskcuts)
        arrposcut=posInCuts[0]
        arrpostcut1=arrposcut+1
        
        xmin=self.df.loc[mask,'epoch'].iloc[0]
        xmax=self.df.loc[mask,'epoch'].iloc[-1]
        xmin=xmin.to_pydatetime()
        xmax=xmax.to_pydatetime()
        #xmin=int(xmin.timestamp() * 1000)/1000
        #xmax=int(xmax.timestamp() * 1000)/1000
        print("xmin={v1} xmax={v2}".format(v1=xmin,v2=xmax))
        xmin=mdates.date2num(xmin)
        xmax=mdates.date2num(xmax)
        print("len(posInCuts)",len(posInCuts[0]))
        print("xmin={v1} xmax={v2}".format(v1=xmin,v2=xmax))
        for idx in range(len(posInCuts[0])):
            print("idx=",idx)
            print("xmin={v1} xmax={v2}".format(v1=xmin,v2=self.df['epoch'].iloc[positionKick[arrposcut[idx]]]))

            rectmin=xmin
            rectmax=self.df['epoch'].iloc[positionKick[arrposcut[idx]]]
            rectmax=rectmax.to_pydatetime()
            rectmax=mdates.date2num(rectmax)
            #rectmax=int(rectmax.timestamp() * 1000)/1000
            #rectmax=mdates.num2date(rectmax)
            width = rectmax - rectmin
            rect = ECERectangle(rectmin, ymin, width, height,
                                    color=color,
                                    index=1)
            rect2 = ECERectangle(xmin, ymin, width, height,
                                     color=color,
                                     index=2)
            rect.setNext(rect2)
            rect2.setPrev(rect)
            self.ax.add_patch(rect)
            self.ax2.add_patch(rect2)
            self.fig.canvas.draw()
            xmin=self.df['epoch'].iloc[positionKick[arrpostcut1[idx]]]
            xmin=xmin.to_pydatetime()
            xmin=mdates.date2num(xmin)
            #xmin=int(xmin.timestamp() * 1000)/1000
            #xmin=mdates.num2date(xmin)

        rectmin=xmin
        rectmax=xmax
        #rectmax=int(rectmax.timestamp() * 1000)/1000
        width = rectmax - rectmin
        rect = ECERectangle(rectmin, ymin, width, height,
                                    color=color,
                                    index=1)
        rect2 = ECERectangle(xmin, ymin, width, height,
                                     color=color,
                                     index=2)
        rect.setNext(rect2)
        rect2.setPrev(rect)
        self.ax.add_patch(rect)
        self.ax2.add_patch(rect2)
        print("xmin={v1} xmax={v2}".format(v1=xmin,v2=xmax))
        self.fig.canvas.draw()




    def getConnection(self, filename):
        """
        get the connection of sqlite given file name
        :param filename:
        :return: sqlite3 connection
        """

        conn = sqlite3.connect(filename)
        return conn
    def readCalibration(self,filename):
        self.dfCal = pd.read_csv(filename)
        print('Results: %s', self.dfCal)
        print('title: %s', self.dfCal['Titles'])
        print('values: %s', self.dfCal['Values'])
        print('ZGain: %s', self.dfCal['Values'][1])
        self.ZOffset=0
        self.ZGain=1
        self.YOffset=2
        self.YGain=3
        self.XOffset=4
        self.XGain=5

    def createCalibrationAction(self):
        image_file='square-upload'
        callback=self.toolbar.importCal
        text="Calibrate"
        tooltip_text="Calibrate"
        a = self.toolbar.addAction(self.toolbar._icon(image_file + '.png'),text, callback)
        print("action created")
        self.toolbar._actions[callback] = a
        print("action added to array")
         
        a.setToolTip(tooltip_text)
    def executeQuery(self, query):
        return None
    def colorChoose(self, r, g, b):
        """
        create a normalized color map give r, g, b in 0-255 scale
        :param r: red
        :param g: green
        :param b: blue
        :return: tuple of color that can be used for matplotlib
        """
        if self.rangeOff(r) or self.rangeOff(g) or self.rangeOff(r):
            return (0, 0, 0)
        return r / 255.0, g / 255.0, b / 255.0

    def rangeOff(self, val):
        return (val > 255) or (val < 0)
    def onpick(self, event):
        print("pick event")
        if isinstance(event.artist, Rectangle):
            patch = event.artist
            # patch.remove()
            self.removedObj = patch
            print('onpick1 patch:', patch.get_path())
        else:
            print(event.artist.get_xdata())
            print(event.artist.get_xdata())
            print(len(event.artist.get_ydata()))
            # self.fig.canvas.draw()
    # def onselect(self, xmin, xmax):
    #     print(xmin)
    #     print(xmax)
    #     width = xmax - xmin
    #     [ymin, ymax] = self.ax.get_ylim()
    #     height = ymax - ymin
    #
    #     rect = matpat.Rectangle((xmin, ymin), width, height,
    #                             fill=True, alpha=0.4,
    #                             color=self.color)
    #     self.ax.add_patch(rect)



    def onclick(self, event):
        if not self.toolbar._actions['zoom'].isChecked() and event.button == 1: # left = 1, middle = 2, right = 3
            self.timeTrack = time.time()
            print("clicked {}".format(self.timeTrack))
            print("clicked X: {}".format(event.xdata))
            self.xpos = event.xdata
            # [ymin, ymax] = self.ax.get_ylim()
            # self.ax.annotate('sth', xy=(event.xdata, event.ydata),
            #                  xytext=(event.xdata, ymax),
            #                  arrowprops=dict(facecolor='black', shrink=0.05),)
            # self.fig.canvas.draw()


    def onrelease(self, event):
        if not self.toolbar._actions['zoom'].isChecked() \
                and event.button == 1 and self.isAnnotate:
                #and not self.toolbar._actions['pan'].isChecked() \
                
                
            curTime = time.time()
            if (curTime - self.timeTrack) > PRE_DEF_CLICK_TIME:
                print("dragged")
                xmin = self.xpos
                xmax = event.xdata
                width = xmax - xmin
                # print(xmin)
                # print(xmax)
                # print(type(xmin))
                # print(mdates.num2date(xmin))
                # print(mdates.num2date(xmax))
                # print(type(xmax))
                # print(width)
                [ymin, ymax] = self.ax.get_ylim()
                height = ymax - ymin

                #annotation problem temporary
                # print(any(cond))
                self.create_annotation(xmin, xmax)
                # print(height)
                rect = ECERectangle(xmin, ymin, width, height,
                                    color=self.color,
                                    index=1)
                rect2 = ECERectangle(xmin, ymin, width, height,
                                     color=self.color,
                                     index=2)
                    # Rectangle((xmin, ymin), width, height,
                    #                     fill=True, alpha=0.4,
                    #                     color=self.color, picker=True)
                rect.setNext(rect2)
                rect2.setPrev(rect)
                self.ax.add_patch(rect)
                self.ax2.add_patch(rect2)

                # self.ax2.add_patch(rect)
                self.fig.canvas.draw()

    def onpress(self, event):
        # print(event.key())
        print(event.key)
        if event.key == 'r':
            self.annoteText = "Kick"
            self.color = self.colorChoose(255, 0, 0)
        elif event.key == 'b':
            self.annoteText = "Sleep"
            self.color = self.colorChoose(0, 0, 255)
        elif event.key == 'g':
            self.annoteText = "Random"
            self.color = self.colorChoose(0, 255, 0)
        elif event.key == "right":
            print("right pressed")
            self.startX += self.currentDelta
            self.endX += self.currentDelta
            self.ax2.set_xlim(self.startX, self.endX)
            # mask = (self.df["epoch"] >= self.startX) & \
            #        (self.df["epoch"] <= self.endX)
            # self.ax2.plot(self.df.loc[mask, "epoch"],
            #               self.df.loc[mask, "mag"], '#1f77b4')
            self.run()
        elif event.key == "left":
            # TODO check left and right limit
            print("left pressed")
            self.startX -= self.currentDelta
            self.endX -= self.currentDelta
            self.ax2.set_xlim(self.startX, self.endX)
            # mask = (self.df["epoch"] >= self.startX) & \
            #        (self.df["epoch"] <= self.endX)
            # self.ax2.plot(self.df.loc[mask, "epoch"],
            #               self.df.loc[mask, "mag"], '#1f77b4')
            self.run()
        elif event.key == "delete":
            print("delete")
            if self.removedObj is not None:
                if isinstance(self.removedObj, ECERectangle):
                    print("deleting ECERect")
                    rect_min_x = self.removedObj.get_x()
                    rect_max_x = rect_min_x + self.removedObj.get_width()
                    self.remove_annotation(rect_min_x, rect_max_x)
                    ind = self.removedObj.getIndex()
                    self.removedObj.remove()
                    if ind == 1:
                        nextRect = self.removedObj.getNext()
                    else:
                        nextRect = self.removedObj.getPrev()
                    self.removedObj = None
                    # print(type())
                    if nextRect.axes is not None:
                        nextRect.remove()
                    self.fig.canvas.draw()

    def run(self):
        self.fig.canvas.draw()
    def create_annotation(self, xmin, xmax):
        print("Annoated")
        cond = self.get_x_in_ranges(xmin, xmax)
        self.df.loc[cond, 'annotated'] = self.annoteText
        self.df.loc[cond, 'colorHex'] = self.get_color_in_hex()

    def remove_annotation(self, xmin, xmax):
        cond = self.get_x_in_ranges(xmin, xmax)
        self.df.loc[cond, 'annotated'] = " "
        self.df.loc[cond, 'colorHex'] = " "

    def get_x_in_ranges(self, xmin, xmax):
        return (self.df["epoch"] <= mdates.num2date(xmax)) \
               & (self.df["epoch"] >= mdates.num2date(xmin))
    def get_color_in_hex(self):
        return "#{:02X}{:02X}{:02X}".format(int(self.color[0] * 255),
                                            int(self.color[1] * 255),
                                            int(self.color[2] * 255))
    def setSelect(self):
        self.isAnnotate = not self.isAnnotate

    def cursorOnclick(self,event):
        'on button press we will see if the mouse is over us '
        if(self.ax==event.inaxes) and (not self.isAnnotate):
            xdata = event.xdata
            dateclicked=mdates.num2date(xdata)
            self.startX = dateclicked
            dateEnd = dateclicked + self.currentDelta
            self.endX = dateEnd
            # df2,epoch,endDate=self.createBottomGraph(dateclicked)

            # mask = (df2["epoch"] >= dateclicked) & (df2["epoch"] <= endDate)
            # self.ax2.clear()
            # self.ax2.set_ylim(1, 1.1)
            # self.ax2.plot(df2.loc[mask, "epoch"], df2.loc[mask, "mag"])
            mask = (self.df["epoch"] >= dateclicked) & (self.df["epoch"] <= dateEnd)
            tX = self.df.loc[mask, "epoch"]
            # print(tX)
            self.ax2.set_xlim(tX.iloc[0], tX.iloc[len(tX) - 1])
            # locator = mdates.SecondLocator(interval=120)
            self.ax2.get_xaxis().set_major_locator(LinearLocator(numticks=12))
            # self.ax2.xaxis.set_major_locator(locator)
            # self.ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

            # self.ax2.relim()
            self.ax2.autoscale_view(True,True,True)
            #
            # x_ticks = np.append(self.ax2.get_xticks(), mdates.date2num(df2.iloc[0,0]))
            # x_ticks = np.append(x_ticks,mdates.date2num(df2.iloc[-1,0]))
            #self.ax2.set_xticks(x_ticks)
            # #self.ax2.tick_params(axis='x', labelsize=8,rotation=45)
            #
            width=mdates.date2num(dateEnd)-xdata
            [ymin, ymax] = self.ax.get_ylim()
            height = ymax - ymin
            if self.rect is not None:
                self.rect.remove()
            self.rect = Rectangle((xdata, ymin), width, height,
                                        fill=True, alpha=0.4,
                                        color=(1,0,0), picker=False)




            self.ax.add_patch(self.rect)

            self.fig.canvas.draw()

    def oncheck(self,label):
        if label == 'valuex':
            self.lx.set_visible(not self.lx.get_visible())
        elif label == 'valuey':
            self.ly.set_visible(not self.ly.get_visible())
        elif label == 'valuez':
            self.lz.set_visible(not self.lz.get_visible())
        elif label == 'mag':
            self.lm.set_visible(not self.lm.get_visible())
        self.fig.canvas.draw()
            
    def changeScale(self,label):
        index = self.labels.index(label)
        self.currentDelta = self.scaleDeltaArray[index]
'''      
    def onmouseover(self,event):
        if event.inaxes == self.ax:
            xdataTest = event.xdata
            dateclickOn=mdates.num2date(xdataTest)
            idx=self.df['epoch'].searchsorted(dateclickOn)
            idx=idx-1
            #logger.debug("dateclickOn:%s idx=%s", dateclickOn,idx)
            vx=self.df['valuex'].values[idx][0]
            vy=self.df['valuey'].values[idx][0]
            vz=self.df['valuez'].values[idx][0]
            vm=self.df['mag'].values[idx][0]
            #print("d: {:%H:%M:%S} vx:{:1.5f} vy:{:1.5f} vz:{:1.5f}".format(dateclickOn,vx,vy,vz))
            #self.txt.set_text('%H:%M:%S x=%1.3f, y=%1.3f, z=%1.3f' % (dateclickOn,vx, vy,vz))
            self.txt.set_text("{:%H:%M:%S} M:{:1.3f}".format(dateclickOn,vm))
            self.fig.canvas.draw()
            self.cursor.onmove(event)
    '''
    # def createBottomGraph(self,startDate):
    #
    #     endDate=startDate + self.currentDelta
    #     query="SELECT * from acc where epoch between {start} and {end} ".\
    #         format(start=startDate.timestamp()*1000, end=endDate.timestamp()*1000)
    #     df2 = pd.read_sql_query(query, self.conn)
    #     df2['epoch']=pd.to_datetime(df2['epoch'], unit='ms')
    #
    #     datevalues= df2['epoch'].dt.to_pydatetime()
    #
    #     df2["mag"] = np.sqrt(np.square(df2["valuex"]) + np.square(df2['valuey']) + \
    #                         np.square(df2["valuez"]))
    #     return (df2,datevalues,endDate)
# initalize figure

#
# print(df)
# print(df["epoch"])
#plt.figure()
# plt.plot([1, 2, 3], [3, 4, 5])
# plt.plot(df["epoch"], df["valuex"])
# plt.plot(df["epoch"], df["valuey"])
# plt.plot(df["epoch"], df["valuez"])

# span = SpanSelector(self.ax, onselect, 'horizontal', useblit=True,
#                     rectprops=dict(alpha=0.5, facecolor='red'))

# ece = ECE4012()
# ece.run()
'''
if __name__ == "__main__":
    print("hello")
    f=plt.figure(1)
    ece=ECE4012(f,"../data/data1pam4v2.csv",None)
    ece.initializer("CSV")
    plt.show()
'''
