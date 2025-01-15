import os
import sys

import numpy as np
import time

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *


class DaqUpdater(QObject):
    
    def __init__(self, controller, controlpanel):
        super().__init__()
        
        self.controller = controller

        self.controlpanel = controlpanel
        
        self.time = time.time()
        
        self.controlpanel.daq_turn_on.pressed.connect(self.daq_change_state)

        self.controller.waveformUpdate.connect(self.visual_updated)
        self.controller.latestFrameNumber.connect(self.update_frame_num)
        
    def daq_change_state(self):
        """
        Due to the new way pycytospectrum works and the fact that the mainboard turns on and off 
        different boards, the best way to do this is to let the main board turn on everything with 
        apply then "close" the previous set of items and "open" all new devices for granite.
        """ 
        if self.controlpanel.daq_turn_on.text() == "Connect DAQ":
            self.controller.open_connection()
        # elif self.controlpanel.daq_turn_on.text() == "Disconnect DAQ":
        else:
            self.controller.close_connection()
    
    def update_frame_num(self, string):
        """!
        This method is connected to the latest_frame_number signal and updates the 
        frame_total_label either with frame number for the player or events for the daq
        
        Assigns: None
        
        Inputs: None
        Outputs: None
        """
        self.controlpanel.frame_total_label.setText(string)

    #TODO:  Make a second one for player one for live
    def visual_updated(self, visual):
        """!
        This method is connected to a visual update event, and updates the waveform

        Assigns: None

        Inputs: None
        Outputs: None
        """
        #TODO:  Eventually move the timer class into its own location and then just use it where 
        #       needed instead of trying to call the time library regularly
        #TODO:  Come up with a good way to update the trigger channel if the player is connected
        # if self.time <= time.time():
        #     self.time += (1/30)
        try:
            self.controlpanel.waveform_curves.setData(y=visual['adc_data'][:,self.controlpanel.trigger_channel])
        except:
            #NOTE:  This only exists now because the hardware has a different way to tell what 
            #       boards are connected and doesn't user serial numbers like the software does, 
            #       this is planned to be removed at some later date
            if self.controlpanel.trigger_channel >= 12:
                self.controlpanel.trigger_channel -= 12
                #TODO: Might want to add an error print out here