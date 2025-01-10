import os
import sys

import pyqtgraph as pg
import numpy as np
from scipy.signal import savgol_filter
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QObject
from multiprocessing.pool import ThreadPool as pool

import time

# pg.setConfigOptions(useOpenGL=True)

class OscilloscopeUpdater(QObject):
    def __init__(self, controller, oscilloscope):
        super().__init__()
        self.ov = oscilloscope
        
        #TODO:  Set this up the same way that it is setup for the control panel
        self.controller = controller
        self.p = pool(12)
        
        self.time = time.perf_counter()
        
        self.waveform_curves = []
        self.eq_points = []
        self.window_size = int(self.ov.window_size.value())
        
        # self.connect_signals()

        self.ov.window_size.valueChanged.connect(self.update_frame)
        self.ov.customContextMenuRequested.connect(self.customMenu)
    
        self.ov.adc_waveform_button.clicked.connect(self.ov.update_channel_names)
        self.ov.photon_waveform_button.clicked.connect(self.ov.update_channel_names)
        self.controller.waveformUpdate.connect(self.visual_updated)

        #NOTE:  This will need probably not exist when the whole program is running since control 
        #       panel will handle it
        self.controller.daqConnection.connect(self.ov.main.switch_connect_button)
        
        print("Oscilloscope Updater setup")

    def test_connect(self):
        print("test")
        
    #TODO:  This only exists to allow connection to the daq this does not need to be here long term
    def daq_change_state(self, status):
        """
        This exists at this time to allow the oscilloscope to connect to a daq without any extra 
        help, at this time the connection button or whatever is used will live in the main thread/on 
        the main window only for the oscilloscope. This function might be used at some later time
        """ 
        if status == "connect":
            self.controller.open_connection()
        else:
            self.controller.close_connection()
        
    #   NOTE:   This is an attempt to add a right click menu, this logic will be used later to 
    #           remove the gate button logic
    def customMenu(self, event):
        """!
        This method sets up the right click menu inside of the plot widget
        
        Assigns:
        
        Inputs:
            event:      Right click event
        Outputs:        
        """
        self.menu = QtWidgets.QMenu(self)
        
        add_line_x = self.menu.addAction("Add Horizontal Line")
        add_line_y = self.menu.addAction("Add Vertical Line")
        remove_line_x = self.menu.addAction("Remove Horizontal Line")
        remove_line_y = self.menu.addAction("Remove Vertical Line")
        remove_all_lines = self.menu.addAction("Remove All Lines")
        
        add_line_x.triggered.connect(lambda: self.ov.add_line('x'))
        add_line_y.triggered.connect(lambda: self.ov.add_line('y'))
        remove_line_x.triggered.connect(lambda: self.ov.remove_line('x'))
        remove_line_y.triggered.connect(lambda: self.ov.remove_line('y'))
        remove_all_lines.triggered.connect(lambda: self.ov.remove_line('all'))
        
        self.menu.popup(QtGui.QCursor.pos())

    def update_frame(self):
        self.window_size = int(self.ov.window_size.value())
        self.ov.window_time.setText(f"{8*self.window_size} ns")

    def visual_updated(self, visual):
        """!
        This method is connected to a visual update event from the controller
        """
        if self.ov.shown == None:
            return
        # adc_waveform = wave_set["adc_data"]
        adc_waveform = visual['adc_data'] * 0.6
        photon_waveform = visual["count_data"]
        count = len(adc_waveform[0])

        #NOTE:  No need to enumerate we just save the information which we can use to setup the 
        #       number of channels and will only update the keys if there is a change in number of 
        #       total keys (this also covers if the two for loops that were hiding keys if they
        #       didn't exist or setting up new keys)s
        if (not self.waveform_curves) or (len(self.ov.channels_selected) != len(self.waveform_curves)):
            #NOTE:  We reset on the chance that we want to reduce from 60 channels to some other 
            #       number or increase from 12 to 60, this is only based on inputs
            self.waveform_curves = []
            [self.waveform_curves.append(self.ov.backend_worker.waveform_plot.plot(pen=self.ov.colors[n])) for n in range(len(self.ov.channels_selected))]
        if (not self.eq_points) or (len(self.ov.photon_names) != len(self.eq_points)):
            self.eq_points = []
            [self.eq_points.append(0) for n in range(len(self.ov.photon_names))]

        if self.ov.shown == "ADC":
            self.p.apply(self.show_waveform_adc, args=(adc_waveform.T, count))
        elif self.ov.shown == "Photon":
            self.p.apply(self.show_waveform_photon, args=(photon_waveform.T, count))
            
            if (self.ov.backend_worker.eq_window.isHidden() == False):
                self.ov.backend_worker.equalizer.setValues(self.eq_points)

    def smooth_wave(self, wave):
        """!
        This method is called to smooth the line that will be output for the user in the photon view

        Assigns: None

        Inputs:
            wave        (List) list of photon counts
        Outputs: None
        """
        temp = np.array(wave, dtype=float)
        if self.window_size > len(temp):
            return temp
        smoothedWave = savgol_filter(x=temp, window_length=self.window_size, polyorder=1)
        return smoothedWave
    
    def show_waveform_adc(self, adc_waveform, count):
        for n in range(count):
            if self.ov.channels_selected[n].isChecked():
                self.waveform_curves[n].setData(y=adc_waveform[n])
            else:
                self.waveform_curves[n].setData(y=np.array([0]))

    def show_waveform_photon(self, photon_waveform, count):
        for n in range(count):
            if self.ov.channels_selected[n].isChecked():
                smoothedWave = self.smooth_wave(photon_waveform[n])
                self.waveform_curves[n].setData(y=smoothedWave)
            else:
                self.waveform_curves[n].setData(y=np.array([0]))
            self.eq_points[n] = np.sum(photon_waveform[n])