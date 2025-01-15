import sys
import os
import numpy as np
import scipy.stats as stats
import pyqtgraph as pg
import time
from math import ceil
from PyQt6 import QtCore, QtGui
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import (QGridLayout, QVBoxLayout, QSplitter, QGroupBox, QLabel, QComboBox, 
                             QDoubleSpinBox, QDockWidget, QTableWidget, QTableWidgetItem, QWidget, 
                             QPushButton)
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtCore import QThread, QObject, pyqtSignal
from pyqtgraph.graphicsItems.ROI import ROI
from pyqtgraph.graphicsItems import ROI

#TODO:  Make this cleaner
channel_groups = {0: "adc_data", 1: "count_data"}
trigger_types = {0: "rising", 1: "falling", 2: "envelope", 3: "auto", 4: "always-on"}
nbins_types = {0:'64', 1:'128', 2:'256', 3:'512', 4:'1024'} #, 4:'2048', 5:'4096'}
baseline_types = {0: "mean-subtracted", 1: "min-subtracted", 2: "baseline", 3: "manual-baseline", 4:"raw"}
signal_treatment_types = {0:"smoothed", 1: "compressed", 2:"compressed-smooth", 3:"raw"}
compression_ratio_types = {0:'1', 1:'2', 2:'4', 3:'8', 4:'16', 5:'32', 6:'64'}

class ScatterProcessor(QObject):
    def __init__(self, channelScatterPlot):
        super().__init__()

        self.sp = channelScatterPlot
        
        self.parameter_changed()

    def parameter_changed(self):
        self.ch1 = self.sp.ch1select.currentIndex()
        self.ch2 = self.sp.ch2select.currentIndex()
        self.trigger_threshold = self.sp.triggerthreshselect.value()
        self.trigger_channel = self.sp.triggerchannelselect.currentIndex()
        self.trigger_type = trigger_types[self.sp.triggertypeselect.currentIndex()]
        self.nbins = int(nbins_types[self.sp.nbinsselect.currentIndex()])
        self.ch1_baseline_method = baseline_types[self.sp.ch1_baselineselect.currentIndex()]
        self.ch2_baseline_method = baseline_types[self.sp.ch2_baselineselect.currentIndex()]
        self.compression_ratio = compression_ratio_types[self.sp.crselect.currentIndex()]
        self.signal_treatment = signal_treatment_types[self.sp.stselect.currentIndex()]