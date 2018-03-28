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
# import os
# import random
import matplotlib
from ece4012 import ECE4012
matplotlib.use('Qt5Agg')
# Make sure that we are using QT5
from PyQt5 import QtCore, QtWidgets

from numpy import arange, sin, pi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
# from matplotlib.backend_bases import NavigationToolbar2 as NavigationToolbar
# progname = os.path.basename(sys.argv[0])
# progversion = "0.1"

class MyNavigationToolbar(NavigationToolbar):
    def __init__(self, canvas, parent, fig):
        self.ece = None
        # self.canvas = canvas
        # self.parent = parent
        # C:\Python36\Lib\site-packages\matplotlib\mpl-data\images is the directory
        # you want to put image as (name)_large.png. it should be 48 x 48.
        # for people using anaconda the directory is:
        # C:\Users\"YourUserName"\Anaconda3\Lib\site-packages\matplotlib\mpl-data\images
        self.fig = fig
        self.toolitems = (
            ("ImportDB", "Import DB file", "import", "importDB"),
            ('Home', 'Reset original view', 'home', 'home'),
            ('Back', 'Back to  previous view', 'back', 'back'),
            ('Forward', 'Forward to next view', 'forward', 'forward'),
            # (None, None, None, None),
            ("Hello", "Hello", "music", 'hello'),
            ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
            # (None, None, None, None),
             ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
            ('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),
            # (None, None, None, None),
            ('Save', 'Save the figure', 'filesave', 'save_figure'),
            ("Export", "Export DB to CSV", "export", "exportCSV")
        )
        NavigationToolbar.__init__(self, canvas, parent, coordinates=False)

    def hello(self):
        print("Hello")

    def importDB(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None,
                                                            "Choose Your DB",
                                                            "",
                                                            "All Files (*);;Database Files (*.db)",
                                                            options=options)
        # print(fileName)
        if fileName is not None:
            # print("mmm")
            #passing toolbar to ECE4012 class
            self.ece = ECE4012(self.fig, fileName,self)
            self.ece.run()
    def exportCSV(self):
        if self.ece is not None:
            print("nono")
            options = QtWidgets.QFileDialog.Options()
            options |= QtWidgets.QFileDialog.DontUseNativeDialog
            fileName, _ = QtWidgets.QFileDialog.getSaveFileName(None, "Save Your CSV", "", "All Files (*);;CSV Files (*.csv)", options=options)
            self.ece.df.to_csv(fileName, sep=",", encoding='utf-8')
          

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
        sc.setFocusPolicy( QtCore.Qt.ClickFocus )
        sc.setFocus()
        # dc = MyDynamicMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        l.addWidget(sc)
        # l.addWidget(dc)
        self.nav = MyNavigationToolbar(sc, self.main_widget, sc.fig)
        l.addWidget(self.nav)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.statusBar().showMessage("All hail matplotlib!", 2000)

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
aw.setWindowTitle("%s" % "ECE4012")
aw.show()
sys.exit(qApp.exec_())
#qApp.exec_()
