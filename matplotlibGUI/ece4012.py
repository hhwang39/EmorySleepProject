import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import time
from matplotlib.widgets import SpanSelector
import matplotlib.patches as matpat
from matplotlib.patches import Rectangle
import random

PRE_DEF_CLICK_TIME = 0.5
class ECE4012:
    def __init__(self):
        self.fig = plt.figure()
        self.fig.canvas.mpl_connect('button_release_event', self.onrelease)
        self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.fig.canvas.mpl_connect('key_press_event', self.onpress)
        self.fig.canvas.mpl_connect('pick_event', self.onpick)
        print(self.fig)
        self.conn = self.getConnection("data.db")
        df = pd.read_sql_query("select * from  acc LIMIT 1000;", self.conn)
        avgX = np.sum(df["valuex"]) / len(df["valuex"])
        avgY = np.sum(df["valuey"]) / len(df["valuey"])
        avgZ = np.sum(df["valuez"]) / len(df["valuez"])
        df["valuex"] = np.subtract(df["valuex"], avgX)
        df["valuey"] = np.subtract(df["valuey"], avgY)
        df["valuez"] = np.subtract(df["valuez"], avgZ)
        df["mag"] = np.sqrt(df["valuex"] * df["valuex"] + df['valuey'] * df['valuey'] + \
                            df["valuez"] * df["valuez"])
        self.ax = self.fig.add_subplot(2, 1, 1)
        self.ax2 = self.fig.add_subplot(2, 1, 2)
        self.ax.plot(df["epoch"], df["mag"], picker=True)
        # self.ax.title("Magnitude")
        self.ax2.plot(df["epoch"], df["valuex"],
                      color=self.colorChoose(255, 0, 255))
        self.ax2.plot(df["epoch"], df["valuey"],
                      color=self.colorChoose(255, 0, 0))
        self.ax2.plot(df["epoch"], df["valuez"],
                      color=self.colorChoose(255, 255, 0))
        self.color = self.colorChoose(random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255))
        self.removedObj = None
        # self.ax.add_patch(rect)
        self.fig.canvas.draw()
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
        if event.button == 1: # left = 1, middle = 2, right = 3
            self.ax.timeTrack = time.time()
            print("clicked {}".format(self.ax.timeTrack))
            print("clicked X: {}".format(event.xdata))
            self.ax.xpos = event.xdata
            # [ymin, ymax] = self.ax.get_ylim()
            # self.ax.annotate('sth', xy=(event.xdata, event.ydata),
            #                  xytext=(event.xdata, ymax),
            #                  arrowprops=dict(facecolor='black', shrink=0.05),)
            # self.fig.canvas.draw()


    def onrelease(self, event):
        if event.button == 1:
            curTime = time.time()
            if (curTime - self.ax.timeTrack) > PRE_DEF_CLICK_TIME:
                print("dragged")
                xmin = self.ax.xpos
                xmax = event.xdata
                width = xmax - xmin
                print(width)
                [ymin, ymax] = self.ax.get_ylim()
                height = ymax - ymin
                print(height)
                rect = matpat.Rectangle((xmin, ymin), width, height,
                                        fill=True, alpha=0.4,
                                        color=self.color, picker=True)
                self.ax.add_patch(rect)
                self.fig.canvas.draw()

    def onpress(self, event):
        print(event.key)
        if event.key == 'r':
            self.color = self.colorChoose(255, 0, 0)
        elif event.key == 'b':
            self.color = self.colorChoose(0, 0, 255)
        elif event.key == 'g':
            self.color = self.colorChoose(0, 255, 0)
        elif event.key == "delete":
            if self.removedObj is not None:
                self.removedObj.remove()
                self.removedObj = None
                self.fig.canvas.draw()

    def run(self):
        plt.show()




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

ece = ECE4012()
ece.run()

