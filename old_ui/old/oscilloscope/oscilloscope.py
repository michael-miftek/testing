import os
import sys

import pyqtgraph as pg
import numpy as np
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QCheckBox, QGroupBox, QLabel, QPushButton, QRadioButton
from PyQt6.QtCore import QThread

try:
    from oscilloscope_updater import OscilloscopeUpdater
    from backend import Backend
except:
    from .oscilloscope_updater import OscilloscopeUpdater
    from .backend import Backend

import time

class OscilloscopeView(QtWidgets.QWidget):

    """!
    Creates a selectable oscilloscope view.
    """
    def __init__(self, controller, adc_channels, photon_channels, main):
        """
        Inputs:
            daq:
            config:
        """
        super().__init__()

        self.main = main

        self.channels_selected = []
        self.vertical_line = []
        self.horizontal_line = []
        self.waveform_layout = None
        self.shown = None

        #self.colors = pg.ColorMap(pos=None, color=colormaps().channel_colors)
        self.colors = ["black", "red", "blue", "green", "orange", "magenta"] * 24
        
        self.oscilloscope_updater_thread = None
        self.oscilloscope_updater = None

        self.backend_thread = None
        self.backend_worker = None

        self.equalizer = None
        self.eq_window = None

        self.time = time.time()

        self.adc_names = [adc_channels[x][-1] for x in range(len(adc_channels))]
        self.photon_names = [photon_channels[x][-1] for x in range(len(photon_channels))]
        
        self.channel_setup()
        self.frame_selection_setup()
        self.setup_workers(controller)

        self.layout_setup()

        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
    
    def finish(self):
        if self.oscilloscope_updater_thread:
            self.oscilloscope_updater_thread.quit()
        if self.backend_thread:
            self.backend_thread.quit()
        print("Oscilloscope UI backend quit")
    
    def layout_setup(self):
        self.waveform_layout = QHBoxLayout(self)
        channels_layout = QVBoxLayout()

        self.waveformSelectBox.setMaximumWidth(200)
        self.frameSelectionBox.setMaximumWidth(200)
        self.channelSelectBox.setMaximumWidth(200)

        channels_layout.addWidget(self.waveformSelectBox)
        channels_layout.addWidget(self.frameSelectionBox)
        channels_layout.addWidget(self.channelSelectBox)

        self.waveform_layout.addWidget(self.backend_worker.waveform_plot)
        self.waveform_layout.addLayout(channels_layout)

    def setup_workers(self, controller):
        self.backend_worker = Backend(self)
        self.backend_thread = QThread()
        self.backend_worker.moveToThread(self.backend_thread)
        
        self.oscilloscope_updater = OscilloscopeUpdater(controller, self)
        self.oscilloscope_updater_thread = QThread()
        self.oscilloscope_updater.moveToThread(self.oscilloscope_updater_thread)

    def channel_setup(self):
        self.channelSelectBox = QGroupBox("Channel Select")
        verticalLayout = QVBoxLayout()

        for ch in range(len(self.adc_names)):
            self.channels_selected.append(QCheckBox(text=f"{self.adc_names[ch]}"))
            verticalLayout.addWidget(self.channels_selected[ch])
            self.channels_selected[ch].setStyleSheet(f"color: {self.colors[ch]}")
    

        self.EQButton = QPushButton("EQ")
        self.EQButton.setFixedSize(100,50)
        
        verticalLayout.addWidget(self.EQButton)

        verticalLayout.addStretch(1)
        self.channelSelectBox.setLayout(verticalLayout)

        self.waveformSelectBox = QGroupBox("Waveform Select")
        verticalLayout = QVBoxLayout()

        self.adc_waveform_button = QRadioButton("ADC waveforms")
        self.adc_waveform_button.setEnabled(True)

        self.photon_waveform_button = QRadioButton("Photon waveforms")
        self.photon_waveform_button.setEnabled(True)

        verticalLayout.addWidget(self.adc_waveform_button)
        verticalLayout.addWidget(self.photon_waveform_button)
        self.waveformSelectBox.setLayout(verticalLayout)

    def frame_selection_setup(self):
        self.frameSelectionBox = QGroupBox("Photon Frame Selection")
        verticalLayout = QVBoxLayout()

        hsplitter1 = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        frametitle = QLabel("Window time")
        self.window_time = QLabel("8 ns")
        hsplitter1.addWidget(frametitle)
        hsplitter1.addWidget(self.window_time)

        hsplitter2 = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        selecttitle = QLabel("Size of window")
        self.window_size = QtWidgets.QDoubleSpinBox()
        self.window_size.setDecimals(0)
        self.window_size.setRange(2,512)
        self.window_size.setSingleStep(1)
        self.window_size.setValue(2)
        hsplitter2.addWidget(selecttitle)
        hsplitter2.addWidget(self.window_size)

        verticalLayout.addWidget(hsplitter1)
        verticalLayout.addWidget(hsplitter2)

        self.frameSelectionBox.setLayout(verticalLayout)

    def update_channel_names(self):
        """!
        This method returns if a channel at location n is checked

        Assigns: None

        Inputs:
            n:          This is the number of the channel to check
        Outputs: None
        """
        if self.adc_waveform_button.isChecked():
            self.photon_waveform_button.setChecked(False)
            for i in range(len(self.adc_names)):
                self.channels_selected[i].setText(self.adc_names[i])    
            self.shown = "ADC"
        elif self.photon_waveform_button.isChecked():
            self.adc_waveform_button.setChecked(False)
            for i in range(len(self.photon_names)):
                self.channels_selected[i].setText(self.photon_names[i])
            self.shown = "Photon"
        else:
            self.shown = None

    def load(self, new_adc_channels, new_photon_channels):
        """!
        This method is called from main when a new channel config file is loaded

        Assigns:
            names:          (list) This is the new list of strings to be shown in the channel box

        Inputs:
            newchannels:    (list) This is the new set tuples that holds the new channel values
        Outputs: None
        """
        self.adc_names = [new_adc_channels[x][-1] for x in range(len(new_adc_channels))]
        self.photon_names = [new_photon_channels[x][-1] for x in range(len(new_photon_channels))]
        self.update_channel_names()