# embedding_in_qt5.py --- Simple Qt5 application embedding matplotlib canvases
#
# Copyright (C) 2005 Florent Rougon
#               2006 Darren Dale
#               2015 Jens H Nielsen
#
# This file is an example program for matplotlib. It may be used and
# modified with no restriction; raw copies as well as modified versions
# may be distributed without limitation.

from __future__ import unicode_literals
import numpy as np
import sys
import os
# import random
import matplotlib
from ece4012 import ECE4012
matplotlib.use('Qt5Agg')
# Make sure that we are using QT5
from PyQt5 import QtCore, QtWidgets

from numpy import arange, sin, pi
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
# from matplotlib.backend_bases import NavigationToolbar2 as NavigationToolbar
# progname = os.path.basename(sys.argv[0])
# progversion = "0.1"

from mydialog import Ui_Dialog as Form

class MyNavigationToolbar(NavigationToolbar):
    def __init__(self, canvas, parent, fig):
        # plt.clf()
        # fig.clear()
        self.ece = None
        # self.canvas = canvas
        # self.parent = parent
        # C:\Python36\Lib\site-packages\matplotlib\mpl-data\images is the directory
        # you want to put image as (name)_large.png. it should be 48 x 48.
        # where to put the images for Anaconda
        # C:\Users\"UserName"\Anaconda3\Lib\site-packages\matplotlib\mpl-data\images
        self.fig = fig
        self.toolitems = (
            # Name, Hover Over Brief Detail, Image, function call
            ("ImportDB", "Import DB file", "import", "importDB"),
            #("ImportCSV", "Import CAV file", "importcsv", "importCSV"),
            ('Home', 'Reset original view', 'home', 'home'),
            ('Back', 'Back to  previous view', 'back', 'back'),
            ('Forward', 'Forward to next view', 'forward', 'forward'),
            # (None, None, None, None),
            #('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
            # (None, None, None, None),
             ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
            ('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),
            # (None, None, None, None),
            ('Save', 'Save the figure', 'camera', 'save_figure'),
            ("Export", "Export DB to CSV", "export", "exportCSV"),
            ("Help", "Help", "question", 'help'),
            ("Annotate", "Enable Annotate", "annotate", "enableAnnotate"),
            ("Calibrate", "Calibrate Your Plot", "calibration", "importCal")
        )
        NavigationToolbar.__init__(self, canvas, parent, coordinates=True)
        self._actions["enableAnnotate"].setCheckable(True)
        
    def enableAnnotate(self):
        if self.ece is not None:
            self.ece.setSelect()
    def drag_pan(self, event):
        if self._xypress:
            x, y = event.x, event.y
            lastx, lasty, a, ind, view = self._xypress[0]
            (x1, y1), (x2, y2) = np.clip(
                [[lastx, lasty], [x, y]], a.bbox.min, a.bbox.max)
            # self._zoom_mode = "x"
            y1, y2 = a.bbox.intervaly
            self.draw_rubberband(event, x1, y1, x2, y2)
    # def hello(self):
    #     print("Hello")

    def importDB(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None,
                                                            "Choose Your DB",
                                                            "",
                                                            "Database Files (*.db);;CSV Files (*.csv);;All Files (*)",
                                                            options=options)
        if fileName:
            print("File opened " + fileName)
            # print(fileName)
            #passing toolbar to ECE4012 class
            self.ece = ECE4012(self.fig, fileName, self)
            self._actions["enableAnnotate"].setChecked(False)
            #self.ece.initializer()
            fn, file_ext = os.path.splitext(fileName)
            if file_ext.lower() == ".csv":
                self.ece.initializer("CSV")
                self.ece.run()
            elif file_ext.lower() == ".db":
                self.ece.initializer("DB")
                self.ece.run()

    def importCSV(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None,
                                                            "Choose Your CSV File",
                                                            "",
                                                            "CSV Files (*.csv);;All Files (*)",
                                                            options=options)
        if fileName:
            print("File opened " + fileName)
            # print(fileName)
            #passing toolbar to ECE4012 class
            self.ece = ECE4012(self.fig, fileName, self)
            self.ece.initializer("CSV")
            self.ece.run()

    def importCal(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None,
                                                            "Choose Your Cal",
                                                            "",
                                                            "All Files (*);;CSV Files (*.csv)",
                                                            options=options)
        # print(fileName)
        #if fileName is not None:
        if fileName:
            # print("mmm")
            try:       
                self.ece.readCalibration(fileName)
                #self.ece.initializer()
                self.ece.redrawAfterCalibrate()
                self.ece.run()
                #aw=QtWidgets.QMainWindow(self.parent)
                #aw.setWindowTitle("%s" % "ECE4012 Calibrated")
                #self.ece.run()
            except:
                raise
    def exportCSV(self):
        if self.ece is not None:
            print("nono")
            options = QtWidgets.QFileDialog.Options()
            options |= QtWidgets.QFileDialog.DontUseNativeDialog
            fileName, _ = QtWidgets.QFileDialog.getSaveFileName(None,
                                                                "Save Your CSV",
                                                                "",
                                                                "CSV Files (*.csv);;All Files (*)",
                                                                options=options)
            if fileName:
                self.ece.df.to_csv(fileName, sep=",", encoding='utf-8')
    def help(self):
        msgBox = QtWidgets.QMessageBox()
        #msgBox.setWindowTitle('Help')
        
        #QtWidgets.QMessageBox.about(None, "Help",
        text="""
        @Copyright Eternal Knights

        To open raw data from MetaWear, click import DB button (yellow arrow icon) and select database file.
        
        To open raw data or exported data as CSV file, click on import DB button, choose from drop down menu .CSV, and select csv file.

        Use home button to return view of bottom graph to original state.
        
        Use left arrow button to undo action taken on GUI.

        Use right arrow button to redo action taken on GUI.

        To zoom in on graph, hover over top graph with selected time scale (30 sec, 5 min, 1 hr, 2hr). Red line will appear and follow mouse cursor.
        Click on starting time position desired for zooming in. To help with selecting area to zoom in, bottom right corner of GUI window shows time frame
        and magnitude of where mouse is hovering over on top graph. Bottom graph will update and scale based on selection.

        To further zoom in on bottom graph, click on magnifying glass button and click and drag on area to zoom in. Magnifying glass is only used for bottom
        graph, not the top graph.

        To pan on zoomed-in graph, use left and right arrow keys on keyboard to show next/previous data points. Panning will scale to selected time scale
        chosen. Ex: With Scale selected as 1 hr, data will pan forward/backwards 1 hr.

        To configure spacing of figures on plots, use the Configure subplots button (sliders icon) to adjust manually how much spacing is desired between
        top and bottom plots along with scale and dataset checkbox.

        To configure axis parameters, use Edit axis, curve and image parameters button (trend arrow icon) to set specifications for x and y axis limits along with
        other options.

        To take a screenshot of GUI with graphs, click on Camera button to take snapshot of what is shown on GUI. Prompt window will appear requesting
        where to save image.

        To export annotated data on GUI, use Export DB to CSV button (blue arrow icon)
        to save all changes to plots as a .csv file.
        
        To annotate, click Enable Annotate button (notebook paper icon). In order to change colors of annotation blocks, press r on keyboard for (Red/Sleep),
        press b on keyboard for (Blue/Sleep), or press g on keyboard for (Green/Random). With button selected, click and drag on bottom graph to create annotation
        blocks on desired area.

        Data shown on both plots will automatically integrate calibration algorithm if calibrationResultsXXXXXXXXXXXX.csv file exists in same directory as imported
        database file. If calibration file does not exist in same directory, use Calibrate Your Plot button (target icon) to open calibrationResultsXXXXXXXXXXXX.csv file.
        """
        #msgBox.setText(text)
        #layout=msgBox.layout
        #msgBox.setMinimumSize(QtCore.QSize(800, 200)) 
        #msgBox.exec_()
        dialog = QtWidgets.QDialog()
        dialog.ui = Form()
        dialog.ui.setupUi(dialog)
        dialog.ui.pushButton.clicked.connect(dialog.close)
        dialog.ui.label.setText(text)
        dialog.exec_()
        dialog.show()
        

    def zoom(self, *args):
        super(NavigationToolbar, self).zoom(*args)
        self._actions['zoom'].setChecked(self._active == 'ZOOM')

    def drag_zoom(self, event):
        """Callback for dragging in zoom mode."""
        if self._xypress:
            x, y = event.x, event.y
            lastx, lasty, a, ind, view = self._xypress[0]
            (x1, y1), (x2, y2) = np.clip(
                [[lastx, lasty], [x, y]], a.bbox.min, a.bbox.max)
            self._zoom_mode = "x"
            if self._zoom_mode == "x":
                y1, y2 = a.bbox.intervaly
            elif self._zoom_mode == "y":
                x1, x2 = a.bbox.intervalx
            self.draw_rubberband(event, x1, y1, x2, y2)

class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        # self.axes = self.fig.add_subplot(111)

        self.compute_initial_figure()

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.fig.canvas.setFocus()
    def compute_initial_figure(self):
        pass


# class MyStaticMplCanvas(MyMplCanvas):
#     """Simple canvas with a sine plot."""
#
#     def compute_initial_figure(self):
#         pass
#         # t = arange(0.0, 3.0, 0.01)
#         # s = sin(2*pi*t)
#         # self.axes.plot(t, s)
#

# class MyDynamicMplCanvas(MyMplCanvas):
#     """A canvas that updates itself every second with a new plot."""
#
#     def __init__(self, *args, **kwargs):
#         MyMplCanvas.__init__(self, *args, **kwargs)
#         timer = QtCore.QTimer(self)
#         timer.timeout.connect(self.update_figure)
#         timer.start(1000)
#
#     def compute_initial_figure(self):
#         self.axes.plot([0, 1, 2, 3], [1, 2, 0, 4], 'r')
#
#     def update_figure(self):
#         # Build a list of 4 random integers between 0 and 10 (both inclusive)
#         l = [random.randint(0, 10) for i in range(4)]
#         self.axes.cla()
#         self.axes.plot([0, 1, 2, 3], l, 'r')
#         self.draw()
#

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")

        # self.file_menu = QtWidgets.QMenu('&File', self)
        # self.file_menu.addAction('&Quit', self.fileQuit,
        #                          QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        # self.menuBar().addMenu(self.file_menu)
        #
        # self.help_menu = QtWidgets.QMenu('&Help', self)
        # self.menuBar().addSeparator()
        # self.menuBar().addMenu(self.help_menu)
        # # self.canvas = MyMplCanvas()
        # self.help_menu.addAction('&About', self.about)

        self.main_widget = QtWidgets.QWidget(self)

        l = QtWidgets.QVBoxLayout(self.main_widget)
        sc = MyMplCanvas(self.main_widget, width=20, height=10, dpi=100)
        sc.setFocusPolicy(QtCore.Qt.ClickFocus)
        sc.setFocus()
        # dc = MyDynamicMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        l.addWidget(sc)
        # l.addWidget(dc)
        self.nav = MyNavigationToolbar(sc, self.main_widget, sc.fig)
        l.addWidget(self.nav)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.statusBar().showMessage("PLM Data Analysis Toolkit", 3000)

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()
    # def keyPressEvent(self, e):
    #     print(e.key())

    def about(self):
        QtWidgets.QMessageBox.about(self, "About",
                                    """embedding_in_qt5.py example
Copyright 2005 Florent Rougon, 2006 Darren Dale, 2015 Jens H Nielsen

This program is a simple example of a Qt5 application embedding matplotlib
canvases.

It may be used and modified with no restriction; raw copies as well as
modified versions may be distributed without limitation.

This is modified from the embedding in qt4 example to show the difference
between qt4 and qt5"""
)


qApp = QtWidgets.QApplication(["H"])

aw = ApplicationWindow()
aw.setWindowTitle("%s" % "PLM Data Analysis Toolkit")
aw.show()
sys.exit(qApp.exec_())
#qApp.exec_()
