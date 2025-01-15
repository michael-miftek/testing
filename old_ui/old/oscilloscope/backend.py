import os
import sys

import pyqtgraph as pg
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QObject

try:
    from equalizer_bar import EqualizerBar
except:
    from .equalizer_bar import EqualizerBar

class Backend(QObject):
    def __init__(self, oscilloscope):
        super().__init__()

        self.oscilloscope = oscilloscope
        self.waveformplot_setup()
        self.setup_eq()

        self.oscilloscope.EQButton.clicked.connect(self.popupEQ)

    def waveformplot_setup(self):
        self.waveform_plot = pg.PlotWidget()
        self.waveform_plot.getPlotItem().getViewBox().disableAutoRange(axis='y')
        self.waveform_plot.getPlotItem().getViewBox().setYRange(-1.1, 1.1)
        self.waveform_plot.getPlotItem().getViewBox().setXRange(0, 2500)
        self.waveform_plot.setBackground('w')
        self.waveform_plot.showGrid(x=True, y=True)
        self.waveform_plot.setLabel('left', "ADC Counts (-1 to +1)")
        self.waveform_plot.setMenuEnabled(False)

    def setup_eq(self):
        """!
        This method setups the EQ visual

        Assigns: None

        Inputs: None
        Outputs: None
        """
        self.eq_window = QtWidgets.QDockWidget("Intensity")
        self.eq_window.setFloating(True)
        self.eq_window.hide()

        self.equalizer = EqualizerBar(60,50)
        self.equalizer.setRange(0,5000)
        self.equalizer.setColors(["#ff0000", "#ff3300", "#ff6600", "#ff9900", "#ffcc00", "#ffff00", "#ccff00", "#99ff00", 
                                  "#66ff00", "#33ff00", "#00FF00"])
        self.eq_window.setMinimumSize(600,400)
        self.equalizer.setDecay(500/50)
        self.equalizer.setDecayFrequencyMs(10)
        
        self.eq_window.setWidget(self.equalizer)

    def add_line(self, ori):
        """!
        This method adds a line to the plot
        
        Assigns:
        
        Inputs:
        Outputs:
        """
        if ori == "x":
            self.horizontal_line.append(pg.InfiniteLine(movable=True, angle=0, pen=(255, 0, 0), span=(0,2), hoverPen=(0,0,0)))
            self.waveform_plot.addItem(self.horizontal_line[len(self.horizontal_line) - 1])
        elif ori == "y":
            self.vertical_line.append(pg.InfiniteLine(movable=True, angle=90, pen=(255, 0, 0), span=(0,2), hoverPen=(0,0,0)))
            self.waveform_plot.addItem(self.vertical_line[len(self.vertical_line) - 1])
        else:
            print("Add line error")
        
    def remove_line(self, ori):
        """!
        This method removes lines in the plot
        
        Assigns:
        
        Inputs:
        Outputs:
        """
        if self.horizontal_line and ori == "x":
            self.waveform_plot.removeItem(self.horizontal_line[len(self.horizontal_line) - 1])
            self.horizontal_line.pop()
        elif self.vertical_line and ori == "y":
            self.waveform_plot.removeItem(self.vertical_line[len(self.vertical_line) - 1])
            self.vertical_line.pop()
        elif (self.vertical_line or self.horizontal_line) and ori == "all":
            for n in range(len(self.horizontal_line)):
                self.waveform_plot.removeItem(self.horizontal_line[n])
            for n in range(len(self.vertical_line)):
                self.waveform_plot.removeItem(self.vertical_line[n])
            self.horizontal_line = []
            self.vertical_line = []
        else:
            print("Remove line error")

    def popupEQ(self):
        """!
        This method shows the eq_window, leaving at this time incase we would like to do more with
        the push button

        Assigns: None

        Inputs: None
        Outputs: None
        """
        print("test")
        self.eq_window.show()