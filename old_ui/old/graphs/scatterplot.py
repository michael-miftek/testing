# This Python file uses the following encoding: utf-8
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

sys.path.append('../..')
from ui.oscilloscope.color_maps import colormaps

try:
    from tableview import TableView
    from scatterplot_backend import ScatterPlotUpdater
except:
    from .tableview import TableView

#NOTE: adding this to silence numpy warnings for the time being, comment this out to check before each push
# import warnings
# warnings.filterwarnings("ignore", category=RuntimeWarning)
# np.set_printoptions(threshold=sys.maxsize)

trigger_types = {0: "rising", 1: "falling", 2: "envelope", 3: "auto", 4: "always-on"}
nbins_types = {0:'64', 1:'128', 2:'256', 3:'512', 4:'1024'} #, 4:'2048', 5:'4096'}
baseline_types = {0: "mean-subtracted", 1: "min-subtracted", 2: "baseline", 3: "manual-baseline", 4:"raw"}
signal_treatment_types = {0:"smoothed", 1: "compressed", 2:"compressed-smooth", 3:"raw"}
compression_ratio_types = {0:'1', 1:'2', 2:'4', 3:'8', 4:'16', 5:'32', 6:'64'}

"""!
@package Channelscatterplot
This module includes the setup of the ScatterPlot tab and related object variables. In this module
a TableView, and a HistogramView are setup. The logic for gates is also written here, labeled as 
roi object in the channelScatterPlot object.
"""

class channelScatterPlot(QtWidgets.QWidget):
    """!
    Container widget for the 2d scatter plot, allows a user to place a gate to show further
    information 
    """
    #TODO:  Fix this to have correct inputs
    def __init__(self, daq, adc_channels):
    # def __init__(self, data_processor, config, adc_channels):
        """
        """
        super().__init__()

        #TODO: Move all extra items into the backend
        self.roi_flag = None
        self.total_events_in_gatecall_x = 0
        self.total_events_in_gatecall_y = 0

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
        self.gate_graph_fs = []
        self.gate_graph_ss = []
        self.roi_data = []
        self.roi_shape = []
        self.roi_label = []
        self.num_roi = 0
        
        #set with a drop down button
        self.num_bins = 256
        self.H = 0
        self.xedges = 0
        self.yedges = 0
        self.data_set = []
        self.sample_size = 2500
        self.update_roi = []
        self.names = [adc_channels[x][-1] for x in range(len(adc_channels))]

        #TODO:  Remove/Fix
        # self.data_processor = data_processor
        self.config = None

        self.roi_table = TableView()

        self.setup_histos()
        self.create_control_box()
        self.setup_layout()
        self.setup_workers(daq)
        
    def finish(self):
        print("Closing Scatterplot")
        if self.scatterplot_backend_thread:
            self.scatterplot_backend.finish()
            self.scatterplot_backend_thread.quit()
        print("Scatterplot Closed")
            
        
    def setup_workers(self, daq):
        self.scatterplot_backend = ScatterPlotUpdater(daq, self)
        self.scatterplot_backend_thread = QThread()
        self.scatterplot_backend.moveToThread(self.scatterplot_backend_thread)

    def setup_layout(self):
        overalllayout = QGridLayout(self)
        plot_box = QGroupBox("Plot")
        layout = QVBoxLayout()
        self.view = pg.PlotWidget()
        self.view.showGrid(True, True)
        self.H, self.xedges, self.yedges = np.histogram2d([],[],bins=self.num_bins)
        #NOTE:  The levels will need to be set probably in the application instead of hard set here
        self.scatterplot = pg.ImageItem(self.H, levels=[0, ceil(self.sample_size/self.num_bins)*2])
        color = colormaps().turbo[::-1]
        cmap = pg.ColorMap(pos=None, color=color)
        self.scatterplot.setColorMap(cmap)
        self.view.addItem(self.scatterplot)
        self.view.setBackground('w')

        # Set the limits of the scatter plot
        self.view.disableAutoRange(axis=pg.ViewBox.XYAxes)
        self.view.setLimits(xMin=0, xMax=self.num_bins, yMin=0, yMax=self.num_bins)
        self.view.setXRange(0,self.num_bins, padding=0)
        self.view.setYRange(0,self.num_bins, padding=0)
        layout.addWidget(self.view)
        plot_box.setLayout(layout)
        
        overalllayout.addWidget(plot_box, 0, 0, -1, 1)
        overalllayout.addWidget(self.control_box, 0, 1, 1, 1)
        self.setLayout(overalllayout)

    def setup_histos(self):
        """!
        This method is called to add each stat to its own list when a gate is added 
        """
        self.gate_graph_popup_window = QDockWidget("Gate Histograms",self)
        self.gate_graph_popup_window.setFloating(True)
        self.gate_graph_popup_window.hide()

    def create_control_box(self):
        """!
        This method is called to setup the control box (Parameters) inside of the scatter plot tab
        """
        #TODO:  Eventually clean this up, methods to create the boxes is not needed
        self.control_box = QGroupBox("Parameters")
        layout = QVBoxLayout()

        hsplitter1 = QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        ch1title = QLabel("X-axis (ordinate)")
        self.ch1select = self.make_channel_select()
        hsplitter1.addWidget(ch1title)
        hsplitter1.addWidget(self.ch1select)

        hsplitter2 = QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        ch2title = QLabel("Y-axis (abcissa)")
        self.ch2select = self.make_channel_select()
        hsplitter2.addWidget(ch2title)
        hsplitter2.addWidget(self.ch2select)
        
        #TODO: Change
        self.channel_1 = self.ch1select.setCurrentIndex(self.config['ch1'])
        self.channel_2 = self.ch2select.setCurrentIndex(self.config['ch2'])

        hsplitter4 = QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        intmodetitle = QLabel("Integration Mode")
        self.intmodeselect = self.make_integration_mode_select()
        hsplitter4.addWidget(intmodetitle)
        hsplitter4.addWidget(self.intmodeselect)

        hsplitter5 = QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        peakidmodetitle = QLabel("Peak Ident Mode")
        self.peakidmodeselect = self.make_peak_identification_select()
        hsplitter5.addWidget(peakidmodetitle)
        hsplitter5.addWidget(self.peakidmodeselect)

        hsplitter6 = QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        triggerchanneltitle = QLabel("Trigger Channel")
        self.triggerchannelselect = self.make_channel_select()
        #TODO:  change
        self.triggerchannelselect.setCurrentIndex(self.config["trigger_channel"])
        hsplitter6.addWidget(triggerchanneltitle)
        hsplitter6.addWidget(self.triggerchannelselect)

        hsplitter7 = QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        triggertypetitle = QLabel("Trigger Type")
        self.triggertypeselect = self.make_trigger_type_select()
        hsplitter7.addWidget(triggertypetitle)
        hsplitter7.addWidget(self.triggertypeselect)

        hsplitter8 = QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        triggerthreshtitle = QLabel("Trigger Threshold")
        self.triggerthreshselect = self.make_trigger_threshold()
        hsplitter8.addWidget(triggerthreshtitle)
        hsplitter8.addWidget(self.triggerthreshselect)

        hsplitter9 = QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        sigtreattitle = QLabel("Signal Treatment")
        self.stselect = self.make_signal_treatment_select()
        hsplitter9.addWidget(sigtreattitle)
        hsplitter9.addWidget(self.stselect )

        hsplitter10 = QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        crtitle = QLabel("Compression Ratio")
        self.crselect = self.make_compression_ratio_select()
        hsplitter10.addWidget(crtitle)
        hsplitter10.addWidget(self.crselect)

        hsplitter11 = QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        ch1bltitle = QLabel("Ch1 baseline method")
        self.ch1_baselineselect = self.make_channel_baseline_select()
        hsplitter11.addWidget(ch1bltitle)
        hsplitter11.addWidget(self.ch1_baselineselect)

        hsplitter12 = QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        ch2bltitle = QLabel("Ch2 baseline method")
        self.ch2_baselineselect = self.make_channel_baseline_select()
        hsplitter12.addWidget(ch2bltitle)
        hsplitter12.addWidget(self.ch2_baselineselect)

        hsplitter16 = QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        binstitle = QLabel("Bins")
        self.nbinsselect = self.make_nbins_select()
        self.nbinsselect.setCurrentIndex(2)
        hsplitter16.addWidget(binstitle)
        hsplitter16.addWidget(self.nbinsselect)

        hsplitter13 = QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        gatestitle = QLabel("Gates")
        self.rect_gates_button = QPushButton("Rectangluar")
        self.ellipse_gates_button = QPushButton("Ellipse")
        self.show_gates_button = QPushButton("Show")
        self.show_gates_button.setEnabled(False)
        self.show_gates_button.setFixedSize(100, 50)
        hsplitter13.addWidget(gatestitle)
        hsplitter13.addWidget(self.show_gates_button)
        hsplitter13.addWidget(self.rect_gates_button)
        hsplitter13.addWidget(self.ellipse_gates_button)

        hsplitter14 = QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        self.reset_button = QPushButton("Reset")
        self.reset_button.setFixedSize(100,50)
        self.gate_remove = QPushButton("Remove")
        self.gate_remove.setFixedSize(100,50)
        hsplitter14.addWidget(self.reset_button)
        hsplitter14.addWidget(self.gate_remove)

        hsplitter15 = QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        hsplitter15.addWidget(self.roi_table)

        layout.addWidget(hsplitter1)
        layout.addWidget(hsplitter2)
        layout.addWidget(hsplitter4)
        layout.addWidget(hsplitter5)
        layout.addWidget(hsplitter6)
        layout.addWidget(hsplitter7)
        layout.addWidget(hsplitter8)
        layout.addWidget(hsplitter9)
        layout.addWidget(hsplitter10)
        layout.addWidget(hsplitter11)
        layout.addWidget(hsplitter12)
        layout.addWidget(hsplitter16)
        layout.addWidget(hsplitter13)
        layout.addWidget(hsplitter14)
        layout.addWidget(hsplitter15)
        self.control_box.setLayout(layout)

    def make_integration_mode_select(self):
        """!
        This method is the setup of the drop down menu for integration mode

        Assigns:    None

        Inputs:      None
        Outputs:     
            imode_select:   (QComboBox) This is the mode select box
        """
        imode_select = QComboBox()
        for item in ["robust", "robust-full", "robust-hm", "robust-fwhm", "height-fwhm"]:
            imode_select.addItem(item)

        return imode_select

    def make_peak_identification_select(self):
        """!
        This method is the setup of the drop down menu for peak indenitifcation

        Assigns: None

        Inputs: None
        Outputs: 
            imode_select:   (QComboBox) This is the peak identification select box
        """
        imode_select = QComboBox()
        for item in ["self-triggered"]:
            imode_select.addItem(item)
        return imode_select

    def make_trigger_type_select(self):
        """!
        This method is the setup of the drop down menu for trigger type

        Assigns:    None

        Inputs:      None
        Outputs:     
            ttmode_select:   (QComboBox) This is the trigger type select box
        """
        ttmode_select = QComboBox()
        for k, item in trigger_types.items():
            ttmode_select.addItem(item)

        revttypes = {v:k for k, v in trigger_types.items()}
        #TODO: change
        ttmode_select.setCurrentIndex(revttypes[self.config['trigger_type']])

        return ttmode_select

    def make_nbins_select(self):
        """!
        This method is the setup of the drop down menu for number of bins

        Assigns:    None

        Inputs:      None
        Outputs:     
            nbins_select:   (QComboBox) This is the nbins select box
        """
        nbins_select = QComboBox()
        for k, v in nbins_types.items():
            nbins_select.addItem(v)

        return nbins_select

    def make_trigger_threshold(self):
        """!
        This method is the setup of the drop down menu for trigger threshold

        Assigns:    None

        Inputs:      None
        Outputs:     
            trigger_value:  (QComboBox) This is the trigger threshold select box
        """
        trigger_value = QDoubleSpinBox()
        trigger_value.setDecimals(3)
        trigger_value.setRange(-0.900000000000000,0.900000000000000)
        trigger_value.setSingleStep(0.001000000000000)
        #TODO:  Change
        trigger_value.setValue(float(self.config['trigger_threshold']))
        
        return trigger_value

    def make_signal_treatment_select(self):
        """!
        This method is the setup of the drop down menu for compression ratio

        Assigns:    None

        Inputs:      None
        Outputs:     
            compression_ratio_select: (QComboBox) This is the compression ratio select box
        """
        signal_treatment_select = QComboBox()
        for k, item in signal_treatment_types.items():
            signal_treatment_select.addItem(item)

        return signal_treatment_select

    def make_compression_ratio_select(self):
        """!
        This method is the setup of the drop down menu for compression ratio

        Assigns:    None

        Inputs:      None
        Outputs:     
            compression_ratio_select: (QComboBox) This is the compression ratio select box
        """
        compression_ratio_select = QComboBox()
        for k, item in compression_ratio_types.items():
            compression_ratio_select.addItem(item)

        return compression_ratio_select

    def make_channel_select(self):
        """!
        This method is the setup of the drop down menu for channel selection

        Assigns:    None

        Inputs:      None
        Outputs:     
            ch_select:  (QComboBox) This is the channel select box
        """
        ch_select = QComboBox()
        for i in range(len(self.names)):
            ch_select.addItem(f"{self.names[i]}")

        return ch_select

    def make_channel_baseline_select(self):
        """!
        This method is the setup of the drop down menu for channel baseline selection

        Assigns:    None

        Inputs:      None
        Outputs:     
            baseline_select:    (QComboBox) This is the baseline select box
        """
        baseline_select = QComboBox()
        for k, v in baseline_types.items():
            baseline_select.addItem(v)

        return baseline_select