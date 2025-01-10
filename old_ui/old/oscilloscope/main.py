import os
import sys

#NOTE:  This is done since the main call is not at the root of the project
sys.path.append("../..")
from service.controller.controller import Controller

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

import configparser as cfp

from oscilloscope import OscilloscopeView

"""
This file will call and setup the oscilloscope in its own GUI to be used
"""
#NOTE:  Might want to remove the player, and just set the daq to none when not connected
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__()

        self.controller = None
        self.controller_thread = None

        self.channel_config_path = 'channelconfig.ini'
        
        self.setup_processors()

        channelconfig = cfp.ConfigParser()
        if os.path.exists(self.channel_config_path):
            channelconfig.read(self.channel_config_path)

        adc_channels = channelconfig.items('adc_channels')
        photon_channels = channelconfig.items('photon_channels')
        
        self.oscilloscope_view = OscilloscopeView(self.controller, adc_channels, photon_channels, self)
        
        self.setup_layout()

        self.turn_daq_on.clicked.connect(self.connect_daq)
        app.aboutToQuit.connect(self.clean_up)

        self.setWindowTitle("Oscilloscope Service")

    def connect_daq(self):
        if self.turn_daq_on.text() == "Connect DAQ":
            self.oscilloscope_view.oscilloscope_updater.daq_change_state("connect")
        elif self.turn_daq_on.text() == "Disconnect DAQ":
            self.oscilloscope_view.oscilloscope_updater.daq_change_state("disconnect")
                

    def switch_connect_button(self, switch):
        if switch == "connect":
            self.turn_daq_on.setText("Disconnect DAQ")
            print("We have connected")
        else:
            self.turn_daq_on.setText("Connect DAQ")
            print("We are disconnected")
            

    def setup_layout(self):
        mainWidget = QWidget()
        main_addition = QGroupBox("Connection")
        boxlayout = QHBoxLayout()
        self.turn_daq_on = QPushButton("Connect DAQ")
        self.turn_daq_on.setFixedWidth(150)
        boxlayout.addWidget(self.turn_daq_on)
        main_addition.setLayout(boxlayout)

        oscilloscope_box = QGroupBox("Oscilloscope")
        oscilloscope_layout = QHBoxLayout()
        oscilloscope_layout.addWidget(self.oscilloscope_view)
        oscilloscope_box.setLayout(oscilloscope_layout)

        total_layout = QGridLayout()
        total_layout.addWidget(main_addition,0,0)
        total_layout.addWidget(oscilloscope_box,1,0)

        mainWidget.setLayout(total_layout)
        self.setCentralWidget(mainWidget)

    def setup_processors(self):
        self.controller = Controller()
        self.controller_thread = QThread()
        self.controller.moveToThread(self.controller_thread)
        self.controller_thread.started.connect(self.controller.run)

        self.controller_thread.start()

    def clean_up(self):
        if self.controller_thread:
            self.controller.finish()
            self.controller_thread.quit()
            
        self.oscilloscope_view.finish()
        print("Oscilloscope Closed")
    
    
if __name__ == "__main__":

    app = QApplication(sys.argv)
    app.setStyle('fusion')
    w = MainWindow()
    w.show()
    app.exec()