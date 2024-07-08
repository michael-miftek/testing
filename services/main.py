import sys
import os
import time

from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QVBoxLayout, QGroupBox, QMainWindow, QApplication
from PyQt6.QtCore import QObject, QThread
import pyqtgraph as pg
from pyqtgraph.graphicsItems import ROI

import zmq

import scipy.stats as stats
import numpy as np
from math import ceil

#NOTE:  These items are used currently the color maps will be needed but the table view is something 
#       that can be added in post if wanted it works smoothly right now 
from color_maps import colormaps

class TwoDHeatMap(QtWidgets.QWidget):
    def __init__(self, spot, config):
        super().__init__()

        self.total_events_x = 0
        self.total_events_y = 0

        self.roi_Nx = []
        self.roi_meanx = []
        self.roi_stdx = []
        self.roi_varx = []
        self.roi_cvx = []

        self.roi_Ny = []
        self.roi_meany = []
        self.roi_stdy = []
        self.roi_vary = []
        self.roi_cvy = []

        self.roi = []
        self.roi_data = []
        self.roi_shape = []
        self.roi_label = []
        self.num_roi = 0
        
        self.num_bins = 256
        self.H = 0
        self.xedges = 0
        self.yedges = 0
        self.data_set = []
        self.sample_size = 2500
        self.update_roi = []

        self.scatter = None
        self.scatterplot = None
        self.spot = spot
        self.config = config

        self.view_setup()
        self.image_setup()
        self.config_update(None)
        
        #-------- Right Click Menu --------#
        self.scatter.setMenuEnabled(False)
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.setup_menu)
        #-------- Right Click Menu --------#

    def config_update(self, config):
        if self.config is None:
            self.config = {}
            self.config["x-data"] = None
            self.config["y-data"] = None
            self.config["gates"] = []
            self.config["bounds"] = []
            self.config["type"] = "pseudo"
        elif config["type"] == "pseudo":
            self.config["x-data"] = config["x-data"]
            self.config["y-data"] = config["y-data"]
            self.config["gates"] = config["gates"]
            self.config["bounds"] = config["bounds"]
            self.config["type"] = "pseudo"
        else:
            print("We need to be able to change the configs with right click menu")
            
        #NOTE: Feel we should emit a signal here to let worksheet know to update the config file
    
    def image_setup(self):
        overalllayout = QVBoxLayout(self)
        overalllayout.addWidget(self.scatter)
        overalllayout.addWidget(self.stats)

        self.setLayout(overalllayout)

        self.setMinimumHeight(300)
    
    def view_setup(self):
        #--------- 2d scatter ---------#
        self.scatter = pg.PlotWidget(title="PseduoColor")
        self.scatter.showGrid(True, True)
        
        self.H, self.xedges, self.yedges = np.histogram2d([],[],bins=self.num_bins)
        self.scatterplot = pg.ImageItem(self.H, levels=[0, ceil(self.sample_size/self.num_bins)*2])
        color = colormaps().turbo[::-1]
        self.cmap = pg.ColorMap(pos=None, color=color)
        self.scatterplot.setColorMap(self.cmap)
        self.scatter.addItem(self.scatterplot)
        self.scatter.setBackground('w')

        # Set the limits of the scatter plot
        self.scatter.disableAutoRange(axis=pg.ViewBox.XYAxes)
        self.scatter.setLimits(xMin=0, xMax=self.num_bins, yMin=0, yMax=self.num_bins)
        self.scatter.setXRange(0,self.num_bins, padding=0)
        self.scatter.setYRange(0,self.num_bins, padding=0)
        
        # self.stats = TableView()
        # self.stats.hide()
    
    def setup_menu(self):
        self.menu = QtWidgets.QMenu(self)

        change_num_bins = self.menu.addMenu("Number of Bins")
        num1 = change_num_bins.addAction("256")
        num2 = change_num_bins.addAction("512")
        num3 = change_num_bins.addAction("1024")
        # num4 = change_num_bins.addAction("2048")
        
        num1.triggered.connect(lambda: self.numbins_changed(256))
        num2.triggered.connect(lambda: self.numbins_changed(512))
        num3.triggered.connect(lambda: self.numbins_changed(1024))
        # num4.triggered.connect(lambda: self.numbins_changed(2048))

        self.menu.popup(QtGui.QCursor.pos())
        
    def numbins_changed(self, binsIn):
        """!
        This method is called whenever the number of bins is changed

        Assigns:
            num_bins:   (int) Number of bins to be used in the 2d histo plot
        
        Inputs: None
        Outputs: None
        """
        self.num_bins = binsIn
        # self.live_update_plot(self.data_set)
    
    def gate_changed(self):
        """!
        This method is connected to the region of the gate being changed, and updates the position
        of the of the gate

        Assigns:
            roi_shape:  (QPainterPath) This is the path of points that make up the gate

        Inputs: None
        Outputs: None
        """
        for i in range(self.num_roi):
            #NOTE:  This update in the line below allows the program to update for all gates that
            #       have been moved instead of all gates all the time, also the signal was changed
            #       from changed to changedfinished which also means that the roi path update is
            #       not getting called hundreds of times a second. This should be the final piece of
            #       the slow down
            if not self.update_roi[i]: 
                continue
            ##  Adding a work around for using shape method there is an isue where it does not 
            #   update with the current position so the stats are only ever around where it was 
            #   originally created regardless of where it has been moved to
            
            #   First we setup the QPainterPath to use the contains method later, but then the
            #   position and the height and width will also need to be grabbed and added to which
            #   ever functin we need to use.
            #   Ellipse and circle  -> addEllipse
            #   Rect                -> addRect
            #   Beacuse we are now working with a 2d histo we have to account for everything being 
            #   transposed
            self.update_roi[i] = False
            path = QtGui.QPainterPath()
            x,y = self.roi[i].pos()
            w,h = self.roi[i].size()

            w *= self.xstep
            h *= self.ystep
            diffx = x - int(x)
            diffy = y - int(y)
            x = self.xedges[int(x)] + (diffx * self.xstep)
            y = self.yedges[int(y)] + (diffy * self.ystep)

            # print(type(self.roi[i]))
            if(isinstance(self.roi[i], ROI.EllipseROI)):
                path.addEllipse(x,y,w,h)
            elif(isinstance(self.roi[i], ROI.RectROI)):
                path.addRect(x,y,w,h)

            self.roi_shape[i] = path  
    
    def safe_divide(self, a, b):
        """!
        This method is a safe divide to prevent and divisons by 0, this prevents warning outputs

        Assigns: None

        Inputs:  
            A:              (float) This is an input number that is the numerator
            B:              (float) This is an input number that is the denominator
        Outputs: 
            0 or divison:   (float) This is the output either returns a float or if it is a division
                            by 0 it returns 0
        """
        if np.isclose(b, 0):
            return 0.
        else:
            return a/b
        
    # def live_update_plot(self):
    def live_update_plot(self,x,y):
        # self.data_set = data
        #NOTE:  Can we have a different number of events in x and y if not then we only want this to 
        #       save once    
        self.total_events_x = len(x)
        self.total_events_y = len(y)
    
        self.H, self.xedges, self.yedges = np.histogram2d(self.pu.data['adc_peak'][0],self.pu.data['adc_peak'][6],bins=self.num_bins)
        self.H, self.xedges, self.yedges = np.histogram2d(x,y,bins=self.num_bins)
        self.scatterplot.updateImage(self.H)


class MainWindow(QtWidgets.QMainWindow):
    """!
    (This is a doxygen style python insert)

    Main window Qt Entity for the whole program - this is the functional
    entry window for the ControlPanel only. It does not launch the prospective 
    UI.  
    """


    def __init__(self, *args, **kwargs):
        pass
        self.port = None
        self.socket = None
        self.twoD = TwoDHeatMap()

        self.setup_zmq_socket()
        self.thread_setup()

        #   Setup the view on the main window
        self.setCentralWidget(self.twoD)

    #NOTE:  This will setup the thread that will run and collect all information and will in turn call live update plot
    def thread_setup(self):
        #NOTE:  Don't think we need to make this part of the class because a QThread will close on its own when the GUI shuts down
        self.listener_worker = Listener(self.twoD, self.socket_worker)
        self.listener_thread = QThread()
        self.listener_worker.moveToThread(self.listener_thread)


    def setup_zmq_socket(self):
        context = zmq.Context(1)
        self.socket_worker = context.socket(zmq.DISH)
        #NOTE:  Set this up with the kvm setup they use
        # https://zguide.zeromq.org/docs/chapter5/#High-Speed-Subscribers-Black-Box-Pattern
        # self.socket = 
        # pass


class Listener(QObject):
    def __init__(self, twoD, socket):
        super().__init__()
        self.twoD = twoD
        self.socket = socket
        self.socket.bind('udp://localhost:9005') #fill with ip and port use udp for RADIO DISH
        self.listening()

    def listening(self):
        while True:

            #NOTE:  Do this on some freq and dont let it hold and wait for new information
            if currTime >= time.time():
                currTime += (1/120)     #This is 120 Hz refresh
                frames = self.socket.recv_multipart()
                if not frames:
                    continue
                print(f"Recieved: {frames}")
                #NOTE:  Add the x and y values you would like to use
                # x = ?
                # y = ?
                # self.twoD.live_update_plot(x, y)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('fusion')
    w = MainWindow()
    w.show()
    app.exec()
