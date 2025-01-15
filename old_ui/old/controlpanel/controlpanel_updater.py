import os
import sys

import numpy as np
import time

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *


class ControlPanelUpdater(QObject):
    """
    This class is now the backend for just the control panel UI, anything that is specific to the 
    autotrigger, the daq, or the mainboard will exist in its own updater class
    """
    def __init__(self, controller, controlpanel):
        super().__init__()

        self.controller = controller
    
        self.controlpanel = controlpanel

        self.controlpanel.play_button.clicked.connect(self.play_clicked)
        self.controlpanel.stop_button.clicked.connect(self.stop_clicked)
        self.controlpanel.pause_button.clicked.connect(self.pause_clicked)
        self.controlpanel.rewind_button.clicked.connect(self.rewind_clicked)
        self.controlpanel.fastforward_button.clicked.connect(self.fastforward_clicked)
        self.controlpanel.seek_button.clicked.connect(self.seek_clicked)
        self.controlpanel.load_button.clicked.connect(self.load_clicked)
        self.controlpanel.capture_button.clicked.connect(self.capture_clicked)
        
        self.controlpanel.atcdselect.currentIndexChanged.connect(self.trigger_channel_update)
        self.controlpanel.atccselect.textChanged.connect(self.trigger_channel_update)
        self.controlpanel.athreshselect.valueChanged.connect(self.update_thresh_line)
        self.controlpanel.ahystselect.valueChanged.connect(self.update_hyst_line)

        self.controller.daqConnection.connect(self.switch_daq_connect_button)

    def switch_daq_connect_button(self, status):
        if status == "connect":
            self.controlpanel.daq_turn_on.setText("Disconnect DAQ")
            self.controlpanel.daq_connection = "DAQ"
            self.set_button_states()
        else:
            if self.controlpanel.com_port_connect.text() == "Disconnect":
                self.controlpanel.daq_connection = "MB"
            self.controlpanel.daq_turn_on.setText("Connect DAQ")
            
    def set_button_states(self):
        """!
        This method is called to update the button states when the control panel is setup, or when
        switching between DAQ and Player
        
        Test to make sure switching actually works as expected
        """
        if(self.controlpanel.daq_connection in ["DAQ", "MB"]):
            self.controlpanel.capture_button.setEnabled(True)
            self.controlpanel.load_button.setEnabled(False)
            self.controlpanel.daq_0.setEnabled(True)
            self.controlpanel.daq_1.setEnabled(True)
            self.controlpanel.daq_2.setEnabled(True)
            self.controlpanel.daq_3.setEnabled(True)
        elif(self.controlpanel.daq_connection == "Player"):
            self.controlpanel.capture_button.setEnabled(False)
            self.controlpanel.load_button.setEnabled(True)
            self.controlpanel.daq_0.setEnabled(False)
            self.controlpanel.daq_1.setEnabled(False)
            self.controlpanel.daq_2.setEnabled(False)
            self.controlpanel.daq_3.setEnabled(False)
        else:
            #NOTE:  This is now a big error condition might need to have a good error printout
            self.controlpanel.capture_button.setEnabled(False)
            self.controlpanel.load_button.setEnabled(False)
            self.controlpanel.daq_0.setEnabled(False)
            self.controlpanel.daq_1.setEnabled(False)
            self.controlpanel.daq_2.setEnabled(False)
            self.controlpanel.daq_3.setEnabled(False)

        self.controlpanel.play_button.setEnabled(False)
        self.controlpanel.stop_button.setEnabled(False)
        self.controlpanel.pause_button.setEnabled(False)
        self.controlpanel.rewind_button.setEnabled(False)
        self.controlpanel.fastforward_button.setEnabled(False)
        self.controlpanel.seek_button.setEnabled(False)
        
    def trigger_channel_update(self):
        """
        This method updates the trigger channel in the controlpanel, this is where all other ui 
        items reach to find the current trigger channel. It is updated here anytime the spinboxes
        change or in the fringe where the communication that the hardware has doesn't match what the 
        software has it is updated in the daq_updater. This will eventually change but needs to 
        exist somewhere that isn't dependent on the something else being connected
        """
        self.controlpanel.trigger_channel = int((self.controlpanel.atcdselect.currentIndex() * 12) + 
                                   int(self.controlpanel.atccselect.value()))
        
    def update_thresh_line(self):
        """
        Update the thresh line position on the control panel graph
        """
        self.thresh_line.setPos(self.athreshselect.value())
        self.hyst_line_top.setPos(self.athreshselect.value() + self.ahystselect.value())
        self.hyst_line_bot.setPos(self.athreshselect.value() - self.ahystselect.value())

    def update_hyst_line(self):
        """
        Update the hysteresis line positions on the control panel graph
        """
        self.hyst_line_top.setPos(self.athreshselect.value() + self.ahystselect.value())
        self.hyst_line_bot.setPos(self.athreshselect.value() - self.ahystselect.value())

    def play_clicked(self):
        """!
        This method is connected to the Play button and calls the play method daqplayer 
        
        Assigns: None
        
        Inputs: None
        Outputs: None
        """
        self.controller.play_command()

    def stop_clicked(self):
        """!
        This method is connected to the Stop button and calls the stop method daqplayer
        
        Assigns: None
        
        Inputs: None
        Outputs: None
        """
        self.controller.stop_command()

    def pause_clicked(self):
        """!
        This method is connected to the Pause button and calls the pause method daqplayer
        
        Assigns: None
        
        Inputs: None
        Outputs: None
        """
        self.controller.pause_command()

    def rewind_clicked(self):
        """!
        This method is connected to the Rewind button and calls the rewind method in daqplayer
        
        Assigns: None
        
        Inputs: None
        Outputs: None
        """
        self.controller.rewind_command()

    def fastforward_clicked(self):
        """!
        This method is connected to the Fast Forward button and calls the fast forward method in 
        daqplayer
        
        Assigns: None
        
        Inputs: None
        Outputs: None
        """
        self.controller.fastforward_command()

    def seek_clicked(self):
        """!
        This method is connected to the Seek button and calls the get method in daqplayer
        
        Assigns: None
        
        Inputs: None
        Outputs: None
        """
        if(self.controlpanel.frame_num_label.isModified):
            frame_num = self.controlpanel.frame_num_label.displayText()
        self.controller.seek_command(int(frame_num))

    def load_clicked(self):
        """!
        This method is conencted to the Load button and calls the load method in the daqplayer,
        also sets the frame total.
        
        Assigns:
            frame_number_total
        
        Inputs: None
        Outputs: None
        """
        if(self.controlpanel.frame_num_label.isModified):
            seek_num = self.controlpanel.frame_num_label.displayText()

        filename = QFileDialog.getOpenFileName(None, "Open", "", "NPY Files (*.npy)")
        if filename[0] != '':
            self.controlpanel.filename_label.setText(filename[0])

        if self.controller.load_recording(filename[0]):
            
            if seek_num:
                self.controller.seek_command(int(seek_num))
            
            self.controlpanel.play_button.setEnabled(True)
            self.controlpanel.stop_button.setEnabled(True)
            self.controlpanel.pause_button.setEnabled(True)
            self.controlpanel.rewind_button.setEnabled(True)
            self.controlpanel.fastforward_button.setEnabled(True)
            self.controlpanel.seek_button.setEnabled(True)

    def capture_clicked(self):
        """!
        This method is connected to the Record button and allows the user to set a descriptive file
        name in a location of choice, it also changes the state of the button (Record -> Recording)
        to signal that Granite is currently recording
        
        Assigns: None
        
        Inputs: None
        Outputs: None
        """
        ##This will allow the user to "create" a file with a .npy extension
        if self.controlpanel.capture_button.text() == 'Record':
            filename = QFileDialog.getSaveFileName(None, "Save File", "", "NPY Files (*.npy)")
            if filename[0] != '':
                self.controlpanel.filename_label.setText(filename[0])
                if self.controller.toggle_recording(filename[0]):
                    self.controlpanel.capture_button.setText('Recording')
                else:
                    print("Error setting up record file")
            else:
                print("You cannot record without setting a file name!")
        else:
            if self.controller.toggle_recording(None):
                #TODO:  Make sure this logic still works out
                self.controlpanel.capture_button.setText('Record')