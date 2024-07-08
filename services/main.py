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
    def __init__(self, config):
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

        self.x = []
        self.y = []

        self.scatter = None
        self.scatterplot = None
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
        
    # def live_update_plot(self):
    def live_update_plot(self,x,y):
        # self.data_set = data
        #NOTE:  Can we have a different number of events in x and y if not then we only want this to 
        #       save once
        #This is used at this time for testing when x,y will be more what is being pulled from the database then we will return to that
        self.x.append(x)
        self.y.append(y)
    
        self.H, self.xedges, self.yedges = np.histogram2d(self.x,self.y,bins=self.num_bins)
        # self.H, self.xedges, self.yedges = np.histogram2d(x,y,bins=self.num_bins)
        self.scatterplot.updateImage(self.H)


class MainWindow(QtWidgets.QMainWindow):
    """!
    (This is a doxygen style python insert)

    Main window Qt Entity for the whole program - this is the functional
    entry window for the ControlPanel only. It does not launch the prospective 
    UI.  
    """


    def __init__(self, *args, **kwargs):
        super().__init__()
        self.port = None
        self.socket = None
        self.twoD = TwoDHeatMap(None)
        self.freqs = [15, 30, 60, 120]

        self.setup_zmq_socket()
        self.thread_setup()

        #   Setup the view on the main window
        self.view_setup()

    def view_setup(self):
        mainWidget = QtWidgets.QWidget()
        full_layout = QtWidgets.QHBoxLayout()
        Vbox = QtWidgets.QVBoxLayout()

        self.feat1 = QtWidgets.QComboBox()
        self.feat2 = QtWidgets.QComboBox()
        for i in range(42):
            self.feat1.addItem(f"Channel {i}")
            self.feat2.addItem(f"Channel {i}")
        self.feat1.currentIndexChanged.connect(self.change_channels)
        self.feat2.currentIndexChanged.connect(self.change_channels)

        self.event_per_second = QtWidgets.QLabel()
        self.event_per_second.setText("Test")
        
        self.readFreq = QtWidgets.QComboBox()
        for i in self.freqs:
            self.readFreq.addItem(f"{i} Hz")
        self.readFreq.currentIndexChanged.connect(self.change_feaq)

        Vbox.addWidget(self.feat1)
        Vbox.addWidget(self.feat2)
        Vbox.addWidget(self.event_per_second)
        Vbox.addWidget(self.readFreq)

        full_layout.addWidget(self.twoD)
        full_layout.addLayout(Vbox)

        mainWidget.setLayout(full_layout)
        self.setCentralWidget(mainWidget)
        self.setWindowTitle("Service test")

    def change_channels(self):
        self.listener_worker.ch1 = self.feat1.currentIndex()
        self.listener_worker.ch2 = self.feat2.currentIndex()

    def change_feaq(self):
        self.listener_worker.freq = self.freqs[self.readFreq.currentIndex()]

    def thread_setup(self):
        self.listener_worker = Listener(self.twoD, self.socket_worker, self)
        self.listener_thread = QThread()
        print("Moving to thread")
        self.listener_worker.moveToThread(self.listener_thread)
        self.listener_thread.started.connect(self.listener_worker.listening)
        self.listener_thread.start()

    def setup_zmq_socket(self):
        context = zmq.Context()
        self.socket_worker = context.socket(zmq.DISH)
        self.socket_worker.bind('udp://*:9005')

    def closeEvent(self, event):
        print("Shutting down thread")
        self.listener_thread.quit()
        sys.exit(0)

class Listener(QObject):
    def __init__(self, twoD, socket, main):
        super().__init__()
        self.twoD = twoD
        self.socket = socket
        self.main = main
        self.currTime = time.time()
        self.socket_setup()
        self.ch1 = 1
        self.ch2 = 1
        self.freq = 15

    def socket_setup(self):
        #NOTE:  For a radio dish the DISH side is expected to join a "group" that is denoted by a 
        #       tag, the radio side also send the tag as the beginning part of the message. Unsure 
        #       if at this time this is fully required? It can be seen as a saftey feature
        tag = ""
        # self.socket.join(tag)

    def listening(self):
        poller = zmq.Poller()
        poller.register(self.socket, zmq.POLLIN)
        while True:
            #NOTE:  Do this on some freq and dont let it hold and wait for new information
            if self.currTime <= time.time():
                self.currTime += (1/self.freq)
                #This is still blocking
                if poller.poll(timeout=1) == zmq.POLLIN:
                    # frames = self.socket.recv_multipart()
                    frames = self.socket.recv_json()
                    if not frames:
                        continue
                    print(f"Recieved: {frames}")
                    #NOTE:  Add the x and y values you would like to use these will be based on ch1 and ch2
                    # x = ?
                    # y = ?
                    # self.twoD.live_update_plot(x,y)
                    self.main.event_per_second.setText(f"{0} Events per second")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('fusion')
    w = MainWindow()
    w.show()
    app.exec()
