import sys
import os
import numpy as np
import pyqtgraph as pg
import time
from math import ceil
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import (QGridLayout, QVBoxLayout, QSplitter, QGroupBox, QLabel, QComboBox, 
                             QDoubleSpinBox, QDockWidget, QTableWidget, QTableWidgetItem, QWidget, 
                             QPushButton)
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtCore import QThread, QObject, pyqtSignal
from pyqtgraph.graphicsItems.ROI import ROI
from pyqtgraph.graphicsItems import ROI

class HistogramView(QtWidgets.QWidget):
    """!
    Container widget for the histogram view of points inside of a user defined gate
    
    """
    def __init__(self, name):
        """!
        Inputs:
            name:       This name is passed in from Channel Scatter Plot, at this time a fixed name
                        is passed in. Full functionality will allow a name to be propagated based 
                        on which gate is being looked at. 
        
        Variables:
            data_set:   This variable is updated with points that are found inside of a user 
                        defined gate.
            bins:       This variable is the number of bins to be used in a histogram, at this time
                        it is a hard coded value of 256.
            name:       This variable stores the name that is passed from Channel Scatter Plot.
        """
        super().__init__()
        self.data_set = None
        self.histbins = 256
        self.name = name
        
        self.histogram_setup()

        overalllayout = QGridLayout(self)
        overalllayout.addWidget(self.histogramWindow)
        self.setLayout(overalllayout)

    def histogram_setup(self):
        """!
        This method is called to seutp the  histogram window and the plot inside that window.
        
        Assigns:
            self.histogramWindow
            self.histogramPlot
        
        Inputs: None
        Outputs: None
        """
        self.histogramWindow = pg.PlotWidget()
        self.histogramWindow.setBackground("w")
        self.histogramWindow.setYRange(min=0, max=500)
        self.histogramWindow.disableAutoRange(axis=pg.ViewBox.YAxis)
        self.histogramWindow.setLimits(xMin=0, xMax=1, yMin=0, yMax=2500)       #need to replace xmax with the largest possible value we can have and then set fixed bins?
        self.histogramWindow.setMouseEnabled(x=False, y=True)                   #should disable scroll zoom on x axis
        self.histogramWindow.showGrid(True, True)
        self.histogramWindow.setLabel('bottom', self.name)
        self.histogramWindow.setLabel('left', "event counts")
        self.histogramWindow.setContentsMargins(0, 0, 50, 0)

        if self.data_set is None:
            hist, bin_edges = np.histogram(0, self.histbins)
        else:
            hist, bin_edges = np.histogram(self.data_set, self.histbins)
        self.histogramPlot = pg.BarGraphItem(x0=bin_edges[:-1], x1=bin_edges[1:], height=hist)
        self.histogramWindow.addItem(self.histogramPlot)

    def live_update_plot(self):
        """!
        This is a method called to update the plot with live information
        
        Assigns:
            self.histogramPlot
        
        Inputs: None
        Outputs: None
        """
        if self.data_set is None:
            nhist, nbin_edges = np.histogram(0, bins=self.histbins)
        else:
            nhist, nbin_edges = np.histogram(self.data_set, bins=self.histbins)
        self.histogramPlot.setOpts(x0=nbin_edges[:-1], x1=nbin_edges[1:], height=nhist)