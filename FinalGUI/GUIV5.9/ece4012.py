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

#Class to create thread that allows to load graphics in background to speed up startup and reduce setup time
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

# Main Class that plots figures and adds functionality to GUI
class ECE4012:
    def __init__(self, figure, filename, toolbar):
        self.dfCal = None
        self.fig = figure
        self.toolbar = toolbar
        self.filename=filename
        self.rect = None
    # Function used to setup graph after class is created or after new data is loaded
    def initializer(self,type):
        self.fig.clear()
        print("clear figure")
        self.fig.subplots_adjust(hspace=1.0)       
        self.annoteText = "annotated"
        self.isAnnotate = False
        self.fig.canvas.mpl_connect('button_release_event', self.onrelease)
        self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.fig.canvas.mpl_connect('key_press_event', self.onpress)
        self.fig.canvas.mpl_connect('pick_event', self.onpick)

        if type == "DB":
            self.searchOpenCalibration(self.filename)
            self.conn = self.getConnection(self.filename)
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
        # Apply calibration if calibration data is loaded        
        if self.dfCal is not None:
            df["valuex"] = np.subtract(df["valuex"],self.dfCal['Values'][self.XOffset])/self.dfCal['Values'][self.XGain]
            df["valuey"] = np.subtract(df["valuey"], self.dfCal['Values'][self.YOffset])/self.dfCal['Values'][self.YGain]
            df["valuez"] = np.subtract(df["valuez"], self.dfCal['Values'][self.ZOffset])/self.dfCal['Values'][self.ZGain]        

        self.fig.subplots_adjust(bottom=0.3,left=0.2,hspace=1.0)
        # setup some constants to be used in Scale Selection panel
        self.labels=['30 sec','5 min','30 min', '1 hr', '2 hr']
        sec30 = pd.Timedelta(30, unit='s')
        min5 = pd.Timedelta(5, unit='m')
        min30 = pd.Timedelta(30, unit='m')
        hr1 =pd.Timedelta(1, unit='h')
        hr2 =pd.Timedelta(2, unit='h')

        # Scale Selection panel made from Radio Buttons 
        self.scaleDeltaArray=[sec30, min5, min30, hr1, hr2]
        self.rax = self.fig.add_axes([0.02, 0.7, 0.11, 0.15])
        self.rax.set_title('Scale')
        self.check = RadioButtons(self.rax, self.labels)
        self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.check.on_clicked(self.changeScale)

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

        
        # Create magnitude value of acceleration data in a dataframe and substract 1g to eliminate gravity
        df["mag"] = np.sqrt(np.square(df["valuex"]) + np.square(df['valuey']) + \
                            np.square(df["valuez"]))-1.0
        print("Normalize")
        ya_min = df.loc[:, "mag"].min() - 0.1
        ya_max = df.loc[:, "mag"].max() + 0.1
        print("y limit (max={:f},min={:f})".format(ya_max,ya_min))

        
        print("Convert Date Time")
        print(df["epoch"].iloc[0])
        print(df["epoch"].iloc[1])
        # Convert epoch to datetime 
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
        
        # Adjusting epoch time to be in Eastern Time Zone 
        df['epoch']=df['epoch'].dt.tz_localize('UTC').dt.tz_convert('America/New_York')
        # Create external numpy array to manage timestamp data to be sure that data will be datetime
        vepoch=df['epoch']
        self.datevalues= vepoch.dt.to_pydatetime()

        # Create annotated and colorHex columns in the dataframe for capturing annotation
        if 'annotated' not in df.columns:
            charArr = np.chararray((len(df["mag"], )), unicode=True)
            charArr[:] = ' '
            df["annotated"] = pd.DataFrame(charArr)
            df["colorHex"] = pd.DataFrame(charArr)
        # Define format for graph ticks
        self.hoursFmt = mdates.DateFormatter('%a-%m-%d %H:%M:%S')
        self.HMSFmt = mdates.DateFormatter('%H:%M:%S')
        # Get total time of the data in hours
        startDate = df["epoch"].iloc[0]
        self.startDate=startDate
        endDate = df["epoch"].iloc[-1]
        totaltime = int(endDate.timestamp() * 1000) - \
                    int(startDate.timestamp() * 1000)
        total_hours = totaltime/1000/3600 #totaltime in hours
        total_minutes=total_hours*60
        print("total hours {:f}".format(total_hours))

        # Create variable to track drag time
        self.timeTrack=0
        # Create variable to track initial click xpos
        self.xpos = 0
        # Create class attribute with the data to be used in the rest of class functions
        self.df = df

        print("Creating Top Graph")
        # First axis  representing Top Graph
        self.ax = self.fig.add_subplot(2, 1, 1)
        # Second axis representing Bottom Graph
        print("Creating Bottom Graph")
        self.ax2 = self.fig.add_subplot(2, 1, 2)
        # Adjust distance between toolbar and graph to give more space
        self.fig.subplots_adjust(bottom=0.145)

        # Adjust distance between toolbar and graph if data is 24 hours or more
        if total_hours > 24:
            self.fig.subplots_adjust(hspace=1.3)
        print("Start Plot Setting")
        
        # Set axis titles to graphs
        self.ax.set_xlabel("Time")
        self.ax2.set_xlabel("Time")
        self.ax.set_ylabel("Acceleration (g)")
        self.ax2.set_ylabel("Acceleration (g)")
        # Adjust y-axis range to maximum and minimum of magnitude
        self.ax.set_ylim(ya_min, ya_max)
        self.ax2.set_ylim(ya_min, ya_max)
        # Set title with word Calibrated if calibration was applied
        bottomtitle='Magnitude Graph for Start Date '+"{:%Y-%m-%d}".format(startDate)
        if self.dfCal is not None:
            bottomtitle='Calibrated '+bottomtitle
        self.ax.set_title(bottomtitle)

        toptitle='Zoomed-In Graph for Start Date '+"{:%Y-%m-%d}".format(startDate)
        if self.dfCal is not None:
            toptitle='Calibrated '+toptitle
        self.ax2.set_title(toptitle)
        
        # Prepare x-axis range to display initially in bottom graph
        start_time = df["epoch"].iloc[0]
        print("start time={v}".format(v=start_time))
        # If data loaded is longer than 1 hour, GUI will show the first hour on bottom graph
        if total_hours>1:
            end_time = start_time + hr1
        elif total_minutes>30:
            end_time = start_time + min30
        elif total_minutes>5:
            end_time = start_time + min5
        else:
            end_time = start_time + sec30
        print("end time={v}".format(v=end_time))
        self.startX = start_time
        self.endX = end_time
        
        # Set x-axis limit with previous selection
        self.ax2.set_xlim(start_time, end_time)
        print("Set Limit")
        # Create data mask with informaton being displayed
        mask = (df["epoch"] >= start_time) & (df["epoch"] <= end_time)
        print("Plotting")
        
        # Plot top graph
        t = time.time()
        # To increase speed to graph, only plot first 4 points and then
        # substitute the data with function set_data, this saves several seconds of load time
        self.plotTop,  = self.ax.plot(df["epoch"].iloc[0:3], df["mag"].iloc[0:3],visible=True)
        self.plotTop.set_data(self.datevalues, df["mag"])
        self.ax.relim()
        self.ax.autoscale_view(True,True,True)
        self.fig.canvas.draw()
        elapsed = time.time() - t
        print("time taken to top graph magnitude was {:f}".format(elapsed))
        
        print(len(df.loc[mask, "epoch"]))
        # Plot bottom graph
        t = time.time()
        # Initially graphs only magnitude
        # To increase speed to graph, only plot first 4 points and then
        # substitute the data with function set_data, this saves several seconds of load time
        self.lm,  = self.ax2.plot(df["epoch"].iloc[0:3], df["mag"].iloc[0:3],visible=True)
        self.lm.set_data(self.datevalues, df["mag"])
        self.ax2.relim()
        self.ax2.autoscale_view(True,True,True)
        self.fig.canvas.draw()
        elapsed = time.time() - t
        print("time taken to bottom graph magnitude was {:f}".format(elapsed))
        t = time.time()
        # Create thread to plot x value in the bottom graph in background mode
        # to avoid startup delay
        try:
            thread1=myThread(1,"valuex",self)
            thread1.start()
        except:
           print("Error: unable to start thread")
        elapsed = time.time() - t
        print("time taken to bottom graph valuex was {:f}".format(elapsed))
        t = time.time()
        # Create thread to plot y value in the bottom graph in background mode
        # to avoid startup delay
        try:
            thread2=myThread(2,"valuey",self)
            thread2.start()
        except:
           print("Error: unable to start thread")
        
        elapsed = time.time() - t
        print("time taken to bottom graph valuey was {:f}".format(elapsed))
        t = time.time()
        # Create thread to plot z value in the bottom graph in background mode
        # to avoid startup delay
        try:
            thread3=myThread(3,"valuez",self)
            thread3.start()
        except:
           print("Error: unable to start thread")
        
        elapsed = time.time() - t
        print("time taken to bottom graph valuez was {:f}".format(elapsed))

        # x in the range
        tX = df.loc[mask, "epoch"]
        self.ax2.set_xlim(tX.iloc[0], tX.iloc[len(tX) - 1])
        # Set tick format and number on top graph
        self.ax.xaxis.set_major_formatter(self.HMSFmt)
        self.ax.get_xaxis().set_major_locator(LinearLocator(numticks=12))
        # Setup format of ticks to Weekday month/day if data is 24 hours or more
        if total_hours>24:
            self.ax.xaxis.set_major_formatter(self.hoursFmt)



        # Rotate labels on x-axis 45 degrees and set font size to 8
        self.ax.tick_params(axis='x', labelsize=8, rotation=45)
        # Select initial random color for random annotation
        self.color = self.colorChoose(random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255))
        self.removedObj = None
        # Refresh the graph
        self.fig.canvas.draw()
        # Prepare graph to display red cursor on top graph
        self.fig.canvas.mpl_connect('motion_notify_event', self.onmouseover)
        self.cursor = Cursor(self.ax, useblit=True, horizOn=False, color='red', linewidth=2)
        self.cursor.connect_event('button_press_event', self.cursorOnclick)

        # Setup initial value for the scale to 30 seconds
        self.currentDelta= pd.Timedelta(30, unit='s')
        # Set tick format and number on bottom graph
        self.ax2.xaxis.set_major_formatter(self.HMSFmt)
        self.ax2.get_xaxis().set_major_locator(LinearLocator(numticks=7))

        
        # Set function to format coordinates to be displayed on bottom right corner
        self.ax.format_coord = self.format_coord
        # Call function to search for annotation in the data
        # if it was loaded from CSV file and graph them
        if type == "CSV" and 'annotated' in df.columns:
            print("calling searchForAnnotation")
            self.searchForAnnotation()

    # Function that derives values to be shown on bottom right corner.
    # It will display Timestamp and magnitude of where cursor is located
    def format_coord(self,x,y):
        dateclickOn=mdates.num2date(x)
        idx=self.df['epoch'].searchsorted(dateclickOn)
        idx=idx-1
        vx=self.df['valuex'].values[idx][0]
        vy=self.df['valuey'].values[idx][0]
        vz=self.df['valuez'].values[idx][0]
        vm=self.df['mag'].values[idx][0]
        return "{:%H:%M:%S} M:{:1.3f}".format(dateclickOn,vm)

    # Function to read calibrationResultsXXXXXXXXXXXX.csv
    # to obtain offset and gain values of x,y, and z-axis
    # from MetaWear device
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

    # Function used to redraw top and bottom graphs
    # with calibrated values applied to x, y, and z values
    def redrawAfterCalibrate(self):

        print("Computing new data")

        #Computes new x, y, and z values with calibration 
        if self.dfCal is not None:
            self.df["valuex"] = np.subtract(self.df["valuex"],self.dfCal['Values'][self.XOffset])/self.dfCal['Values'][self.XGain]
            self.df["valuey"] = np.subtract(self.df["valuey"], self.dfCal['Values'][self.YOffset])/self.dfCal['Values'][self.YGain]
            self.df["valuez"] = np.subtract(self.df["valuez"], self.dfCal['Values'][self.ZOffset])/self.dfCal['Values'][self.ZGain]        
        print("Computing new mag")

        self.df["mag"] = np.sqrt(np.square(self.df["valuex"]) + np.square(self.df['valuey']) + \
                            np.square(self.df["valuez"]))-1.0
        print("setting titles")
        # Bottom Title changed to say Calibrated
        bottomtitle='Magnitude Graph for Start Date '+"{:%Y-%m-%d}".format(self.startDate)
        if self.dfCal is not None:
            bottomtitle='Calibrated '+bottomtitle
        self.ax.set_title(bottomtitle)

        # Top Title changed to say Calibrated
        toptitle='Zoomed-In Graph for Start Date '+"{:%Y-%m-%d}".format(self.startDate)
        if self.dfCal is not None:
            toptitle='Calibrated '+toptitle
        self.ax2.set_title(toptitle)

        print("redraw graph")

        # Refreshes graphs with new data values
        self.plotTop.set_ydata(self.df["mag"])
        self.lm.set_ydata(self.df["mag"])
        self.lx.set_ydata(self.df["valuex"])
        self.ly.set_ydata(self.df["valuey"])
        self.lz.set_ydata(self.df["valuez"])
        self.fig.canvas.draw()




    # Function used to determine where mouse event occurs    
    def onmouseover(self,event):

        if event.inaxes == self.rax:
            None

        if event.inaxes == self.ax:
            self.cursor.onmove(event)

    # Function used to determine if calibration file is found in same directory
    # as GUI application
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
    # Function used to determine if annotations have been applied to
    # recently opened csv file
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

        # Creates mask of locations of annotations
        # Calls reDrawAnnotation to replot rectangles on graphs
        if len(self.df.loc[maskKick,'epoch'])>0:
            self.reDrawAnnotation(maskKick,colorKick)
        if len(self.df.loc[maskSleep,'epoch'])>0:
            self.reDrawAnnotation(maskSleep,colorSleep)
        if len(self.df.loc[maskRandom,'epoch'])>0:
            self.reDrawAnnotation(maskRandom,colorRandom)
        if len(self.df.loc[maskColorRandom,'epoch'])>0:
            self.reDrawAnnotation(maskColorRandom,randomColor)

    # Function used to redraw all annotations seen when
    # opening csv file that has annotations
    def reDrawAnnotation(self,mask,color):
        
        [ymin, ymax] = self.ax.get_ylim()
        height = ymax - ymin

        # Determines index positions of annotations
        positionKick=np.array(self.df.index[mask].tolist())

        # Determines where gaps between annotations occur
        diff=np.subtract(positionKick[1:-1],positionKick[0:-2])
        
        maskcuts=diff>1
        posInCuts=np.where(maskcuts)
        arrposcut=posInCuts[0]
        arrpostcut1=arrposcut+1

        # Initializes first seen annotation
        xmin=self.df.loc[mask,'epoch'].iloc[0]
        xmax=self.df.loc[mask,'epoch'].iloc[-1]
        xmin=xmin.to_pydatetime()
        xmax=xmax.to_pydatetime()

        # converts values to proper time format
        print("xmin={v1} xmax={v2}".format(v1=xmin,v2=xmax))
        xmin=mdates.date2num(xmin)
        xmax=mdates.date2num(xmax)
        print("len(posInCuts)",len(posInCuts[0]))
        print("xmin={v1} xmax={v2}".format(v1=xmin,v2=xmax))

        # For loop used to run through and create rectangles to plot for annotations
        for idx in range(len(posInCuts[0])):
            print("idx=",idx)
            print("xmin={v1} xmax={v2}".format(v1=xmin,v2=self.df['epoch'].iloc[positionKick[arrposcut[idx]]]))

            rectmin=xmin
            rectmax=self.df['epoch'].iloc[positionKick[arrposcut[idx]]]
            rectmax=rectmax.to_pydatetime()
            rectmax=mdates.date2num(rectmax)
            
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
            

        rectmin=xmin
        rectmax=xmax
        
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



    # Sets up sqlite3 connection to database file
    def getConnection(self, filename):
        """
        get the connection of sqlite given file name
        :param filename:
        :return: sqlite3 connection
        """

        conn = sqlite3.connect(filename)
        return conn

    # Old Function used to read calibration file. No longer relevant
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

    # Function used to create calibration button. No longer relevant
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
    # Function to execute query
    def executeQuery(self, query):
        return None
    # Function used to set range of colors
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

    # Function to set range off
    def rangeOff(self, val):
        return (val > 255) or (val < 0)

    # Function to determine event of creating annotations
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
            


    # Function used to check if annotation is selected
    def onclick(self, event):
        if not self.toolbar._actions['zoom'].isChecked() and event.button == 1: # left = 1, middle = 2, right = 3
            self.timeTrack = time.time()
            print("clicked {}".format(self.timeTrack))
            print("clicked X: {}".format(event.xdata))
            self.xpos = event.xdata
            

    # Function used to determine when annotation event occurs
    def onrelease(self, event):
        if not self.toolbar._actions['zoom'].isChecked() \
                and event.button == 1 and self.isAnnotate:
                
                
                
            curTime = time.time()
            if (curTime - self.timeTrack) > PRE_DEF_CLICK_TIME:
                print("dragged")
                xmin = self.xpos
                xmax = event.xdata
                width = xmax - xmin
                
                [ymin, ymax] = self.ax.get_ylim()
                height = ymax - ymin

                
                self.create_annotation(xmin, xmax)
                
                rect = ECERectangle(xmin, ymin, width, height,
                                    color=self.color,
                                    index=1)
                rect2 = ECERectangle(xmin, ymin, width, height,
                                     color=self.color,
                                     index=2)
                    
                rect.setNext(rect2)
                rect2.setPrev(rect)
                self.ax.add_patch(rect)
                self.ax2.add_patch(rect2)

               
                self.fig.canvas.draw()

    # Key commands running from keyboard
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
           
            self.run()
        elif event.key == "left":
            # TODO check left and right limit
            print("left pressed")
            self.startX -= self.currentDelta
            self.endX -= self.currentDelta
            self.ax2.set_xlim(self.startX, self.endX)
            
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
                    
                    if nextRect.axes is not None:
                        nextRect.remove()
                    self.fig.canvas.draw()

    # Redraws graphs
    def run(self):
        self.fig.canvas.draw()

    # Creates annotation to dataframe
    def create_annotation(self, xmin, xmax):
        print("Annoated")
        cond = self.get_x_in_ranges(xmin, xmax)
        self.df.loc[cond, 'annotated'] = self.annoteText
        self.df.loc[cond, 'colorHex'] = self.get_color_in_hex()

    # Deletes annotation labels
    def remove_annotation(self, xmin, xmax):
        cond = self.get_x_in_ranges(xmin, xmax)
        self.df.loc[cond, 'annotated'] = " "
        self.df.loc[cond, 'colorHex'] = " "

    # Obtain mask of range of x values
    def get_x_in_ranges(self, xmin, xmax):
        return (self.df["epoch"] <= mdates.num2date(xmax)) \
               & (self.df["epoch"] >= mdates.num2date(xmin))
    # Get hexdecimal color
    def get_color_in_hex(self):
        return "#{:02X}{:02X}{:02X}".format(int(self.color[0] * 255),
                                            int(self.color[1] * 255),
                                            int(self.color[2] * 255))
    # Unselect annotation when not active
    def setSelect(self):
        self.isAnnotate = not self.isAnnotate

    # Function used to determine what click and hold effect does for annotations
    def cursorOnclick(self,event):
        'on button press we will see if the mouse is over us '
        if(self.ax==event.inaxes) and (not self.isAnnotate):
            xdata = event.xdata
            dateclicked=mdates.num2date(xdata)
            self.startX = dateclicked
            dateEnd = dateclicked + self.currentDelta
            self.endX = dateEnd
            
            mask = (self.df["epoch"] >= dateclicked) & (self.df["epoch"] <= dateEnd)
            tX = self.df.loc[mask, "epoch"]
            
            self.ax2.set_xlim(tX.iloc[0], tX.iloc[len(tX) - 1])
           
            self.ax2.get_xaxis().set_major_locator(LinearLocator(numticks=12))
            
            self.ax2.autoscale_view(True,True,True)
            
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

    # Sets checks on visibility of x,y, and z -axis plots
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

    # Adjust time scale values to plot on bottom graph        
    def changeScale(self,label):
        index = self.labels.index(label)
        self.currentDelta = self.scaleDeltaArray[index]

 

# Debug lines used to test code and plot data without calling matex2.py
'''
if __name__ == "__main__":
    print("hello")
    f=plt.figure(1)
    ece=ECE4012(f,"../data/data1pam4v2.csv",None)
    ece.initializer("CSV")
    plt.show()
'''
