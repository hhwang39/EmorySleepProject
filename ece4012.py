import sqlite3
import pandas as pd
# import matplotlib.pyplot as plt
import numpy as np
import time
# from matplotlib.widgets import SpanSelector
import matplotlib.patches as matpat
from matplotlib.patches import Rectangle
import random
import matplotlib.dates as mdates
from matplotlib.widgets import RadioButtons
from matplotlib.widgets import Cursor

PRE_DEF_CLICK_TIME = 0.5


# class ECERectangle(Rectangle):
#     def __init__(self):
#         Rectangle.__init__()




class ECE4012:
    def __init__(self, figure, filename, toolbar):
        figure.clear()
        figure.subplots_adjust(hspace=1.0)
        self.rect = None
        self.annoteText = "annonated"
        self.fig = figure
        self.toolbar = toolbar
        self.isAnnotate = False
        self.fig.canvas.mpl_connect('button_release_event', self.onrelease)
        self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.fig.canvas.mpl_connect('key_press_event', self.onpress)
        self.fig.canvas.mpl_connect('pick_event', self.onpick)
        # print(self.fig)
        self.conn = self.getConnection(filename)
        # df = pd.read_sql_query("select * from  acc LIMIT 100000;", self.conn)
        df = pd.read_sql_query("select * from  acc LIMIT 100000;", self.conn)
        print("Starting")
        # TODO this calibartion should change to either actual calibration from
        # metawear C
        # print(len(df["valuex"]))
        # avgX = np.sum(df["valuex"]) / len(df["valuex"])
        # avgY = np.sum(df["valuey"]) / len(df["valuey"])
        # avgZ = np.sum(df["valuez"]) / len(df["valuez"])
        # df["valuex"] = np.subtract(df["valuex"], avgX)
        # df["valuey"] = np.subtract(df["valuey"], avgY)
        # df["valuez"] = np.subtract(df["valuez"], avgZ)
        self.axTop = self.fig.add_subplot(2, 1, 1)
        self.axBottom = self.fig.add_subplot(2, 1, 2)
        self.fig.subplots_adjust(bottom=0.3,left=0.3,hspace=0.5)
        self.labels=['30 sec','5 min','30 min', '1 hr', '2 hr']
        self.rax = self.fig.add_axes([0.02, 0.4, 0.11, 0.15])
        self.rax.set_title('Scale')
        self.check = RadioButtons(self.rax, self.labels)
        self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        #self.rcbax = self.fig.add_axes([0.02, 0.7, 0.11, 0.15])
        #self.rcbax.set_title('DataSet')
        #self.checkBox = CheckButtons(self.rcbax, ('valuex', 'valuey', 'valuez'), (False, True, True))
        #self.checkBox.on_clicked(self.oncheck)

        df["mag"] = np.sqrt(np.square(df["valuex"]) + np.square(df['valuey']) + \
                            np.square(df["valuez"]))
        print("Normalize")
        ya_min = df.loc[:, "mag"].min() - 0.1
        ya_max = df.loc[:, "mag"].max() + 0.1
        # print("Normalized")
        # print(type(ya_min))
        # print(ya_max)

        # print(df["mag"])
        # df["mag"] = df["mag"] - 1 # subtract 1g
        charArr = np.chararray((len(df["mag"], )), unicode=True)
        charArr[:] = ' '
        df["annotated"] = pd.DataFrame(charArr)
        df["colorHex"] = pd.DataFrame(charArr)
        #Convert epoch to datetime to see the right value
        print("Convert Date Time")
        print(df["epoch"].iloc[0])
        print(df["epoch"].iloc[1])
        df['epoch'] = pd.to_datetime(df['epoch'], unit='ms')

        # print(df["epoch"])
        # print(type(df['epoch'][0]))
        #Definition of x-axis formatter of tick
        # self.hoursFmt = mdates.DateFormatter('%Y-%m-%d %H:%M:%S') #Week Month/Day H:M:S
        self.hoursFmt = mdates.DateFormatter('%a-%m-%d %H:%M:%S')
        #Get total time of the data in hours
        startDate = df.iloc[0, 0]
        endDate = df.iloc[-1, 0]
        totaltime = int(endDate.timestamp() * 1000) - \
                    int(startDate.timestamp() * 1000)
        total_hours = totaltime/1000/3600 #totaltime in hours

        #create variable to track drag time
        self.timeTrack=0
        #create variable to track initial click xpos
        self.xpos = 0
        self.df = df

        #adjust distance between toolbar and graph to give more space
        self.fig.subplots_adjust(bottom=0.145)
            
        #adjust distance between toolbar and graph if data is 24 hours or more      
        if total_hours > 24:
            self.fig.subplots_adjust(bottom=0.3)
        print("Start Plot Setting")
        self.ax = self.fig.add_subplot(2, 1, 1)
        # second axis
        self.ax2 = self.fig.add_subplot(2, 1, 2)
        # Set default values for x aixs
        ##changed temporary pls ignore
        # self.ax.set_ylim(1, 1.1)
        # self.ax2.set_ylim(1, 1.1)
        #self.ax.set_ylim(0, 8)
        #self.ax2.set_ylim(0, 8)
        self.ax.set_xlabel("Time")
        self.ax2.set_xlabel("Time")
        self.ax.set_ylabel("Acceleration (g)")
        self.ax2.set_ylabel("Acceleration (g)")
        self.ax.set_ylim(ya_min, ya_max)
        self.ax2.set_ylim(ya_min, ya_max)
        # self.ya_min = ya_min
        # self.ya_max = ya_max
        # start date
        # print(type(df["epoch"]))
        # print(len(df["epoch"]))
        # print(df["epoch"])
        # print()
        # TODO we assume time is not empty but it could be good to chek empty
        start_time = df["epoch"].iloc[0]
        print(start_time)
        # print(type(start_time))
        end_time = start_time + pd.Timedelta(hours=1)
        print(end_time)
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
        self.ax.plot(df["epoch"], df["mag"])
        # print(df.loc[mask, "epoch"])
        print(len(df.loc[mask, "epoch"]))
        self.ax2.plot(df.loc[mask, "epoch"], df.loc[mask, "mag"])
        # self.ax.xaxis.set_major_formatter(self.hoursFmt)
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
        self.currentDelta= pd.Timedelta(5, unit='m')
        
    def onmouseover(self,event):

        if event.inaxes == self.rax:
            None
            #logger.debug("click on radiobutton")
            #self.check._clicked(event)
        if event.inaxes == self.ax:
            self.cursor.onmove(event)
            
    def getConnection(self, filename):
        """
        get the connection of sqlite given file name
        :param filename:
        :return: sqlite3 connection
        """
        conn = sqlite3.connect(filename)
        return conn

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
                and not self.toolbar._actions['pan'].isChecked() \
                and event.button == 1 and self.isAnnotate:
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
                rect = matpat.Rectangle((xmin, ymin), width, height,
                                        fill=True, alpha=0.4,
                                        color=self.color, picker=True)
                self.ax.add_patch(rect)
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
            self.startX += pd.Timedelta(hours=1)
            self.endX += pd.Timedelta(hours=1)
            self.ax2.set_xlim(self.startX, self.endX)
            mask = (self.df["epoch"] >= self.startX) & \
                   (self.df["epoch"] <= self.endX)
            self.ax2.plot(self.df.loc[mask, "epoch"],
                          self.df.loc[mask, "mag"], '#1f77b4')
            self.run()
        elif event.key == "left":
            # TODO check left and right limit
            print("left pressed")
            self.startX -= pd.Timedelta(hours=1)
            self.endX -= pd.Timedelta(hours=1)
            self.ax2.set_xlim(self.startX, self.endX)
            mask = (self.df["epoch"] >= self.startX) & \
                   (self.df["epoch"] <= self.endX)
            self.ax2.plot(self.df.loc[mask, "epoch"],
                          self.df.loc[mask, "mag"], '#1f77b4')
            self.run()
        elif event.key == "delete":
            print("delete")
            if self.removedObj is not None:
                if isinstance(self.removedObj, Rectangle):
                    rect_min_x = self.removedObj.get_x()
                    rect_max_x = rect_min_x + self.removedObj.get_width()
                    self.remove_annotation(rect_min_x, rect_max_x)
                    self.removedObj.remove()
                    self.fig.canvas.draw()
                self.removedObj = None

    def run(self):
        self.fig.canvas.draw()
    def create_annotation(self, xmin, xmax):
        cond = self.get_x_in_ranges(xmin, xmax)
        self.df.loc[cond, 'annonated'] = self.annoteText
        self.df.loc[cond, 'colorHex'] = self.get_color_in_hex()

    def remove_annotation(self, xmin, xmax):
        cond = self.get_x_in_ranges(xmin, xmax)
        self.df.loc[cond, 'annonated'] = " "
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
            df2,epoch,endDate=self.createBottomGraph(dateclicked)
            
            mask = (df2["epoch"] >= dateclicked) & (df2["epoch"] <= endDate)
            self.ax2.clear()
            # self.ax2.set_ylim(1, 1.1)
            self.ax2.plot(df2.loc[mask, "epoch"], df2.loc[mask, "mag"])
            
            locator = mdates.SecondLocator( interval=120)
            
            self.ax2.xaxis.set_major_locator(locator)
            self.ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            
            # self.ax2.relim()
            self.ax2.autoscale_view(True,True,True)

            x_ticks = np.append(self.ax2.get_xticks(), mdates.date2num(df2.iloc[0,0]))
            x_ticks = np.append(x_ticks,mdates.date2num(df2.iloc[-1,0]))
            #self.ax2.set_xticks(x_ticks)
            #self.ax2.tick_params(axis='x', labelsize=8,rotation=45)

            width=mdates.date2num(endDate)-xdata
            [ymin, ymax] = self.ax.get_ylim()
            height = ymax - ymin
            if self.rect is not None:
                self.rect.remove()
            self.rect = matpat.Rectangle((xdata, ymin), width, height,
                                        fill=True, alpha=0.4,
                                        color=(1,0,0), picker=True)


            self.ax.add_patch(self.rect)

            self.fig.canvas.draw()
            
    def createBottomGraph(self,startDate):
  
        endDate=startDate + self.currentDelta
        query="SELECT * from acc where epoch between {start} and {end} ".\
            format(start=startDate.timestamp()*1000, end=endDate.timestamp()*1000)
        df2 = pd.read_sql_query(query, self.conn)
        df2['epoch']=pd.to_datetime(df2['epoch'], unit='ms')

        datevalues= df2['epoch'].dt.to_pydatetime()

        df2["mag"] = np.sqrt(np.square(df2["valuex"]) + np.square(df2['valuey']) + \
                            np.square(df2["valuez"]))
        return (df2,datevalues,endDate)
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

