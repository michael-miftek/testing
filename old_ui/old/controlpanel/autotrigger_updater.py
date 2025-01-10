import os
import sys

import numpy as np
import time

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

class AutotriggerUpdater(QObject):
    def __init__(self, autotrigger, controlpanel):
        super().__init__()
        
        self.autotrig = autotrigger
        self.controlpanel = controlpanel

        self.autotrig.triggerUpdate.connect(self.triggerUpdate)
        self.controlpanel.autotriggerselect.stateChanged.connect(self.atparameter_changed)
        self.controlpanel.triggermethodselect.currentIndexChanged.connect(self.atparameter_changed)
        self.controlpanel.lambdaselect.textChanged.connect(self.atparameter_changed)
        self.controlpanel.orderselect.textChanged.connect(self.atparameter_changed)
        self.controlpanel.zselect.textChanged.connect(self.atparameter_changed)
        self.controlpanel.offsetselect.textChanged.connect(self.atparameter_changed)
        self.controlpanel.avgwindowselect.currentIndexChanged.connect(self.atparameter_changed)

    def triggerUpdate(self):
        """!
        This method is called when the auto trigger emits a signal to update the trigger location,
        the new trigger location is updated in the daq settings and on the control panels 
        oscilloscope view

        Assigns: None

        Inputs: None
        Outputs: None
        """
        new_trigger = self.autotrig.get_latest_trigger()
        if new_trigger is None:
            pass
        else:
            self.controlpanel.athreshselect.setValue(new_trigger)
            self.controlpanel.thresh_line.setPos(new_trigger)

    def atparameter_changed(self, _):
        """!
        This method is called when a parameter is changed, and updates with the value(s) given
        
        Assigns: None
        
        Inputs: None
        Outputs: None
        """
        if self.autotrig is not None:
            self.autotrig.update_values(self.current_atsetting(), self.controlpanel.autotriggerselect.isChecked())

        #TODO:  Remove is not needed
        # if self.controlpanel.autotriggerselect.isChecked():
        #     self.controlpanel.atpselect.setEnabled(False)
        #     self.controlpanel.athreshselect.setEnabled(False)
        #     self.controlpanel.ahystselect.setEnabled(False)
        # else:
        #     self.controlpanel.atpselect.setEnabled(True)
        #     self.controlpanel.athreshselect.setEnabled(True)
        #     self.controlpanel.ahystselect.setEnabled(True)

    def current_atsetting(self):
        """!
        This method is called from atparameter_changed, to promulgate autotrigger settings
        
        Assigns: None
        
        Inputs: None
        Outputs:

        self.autotriggerselect = QCheckBox()
        self.triggermethodselect = QComboBox()
        self.lambdaselect = QLineEdit("10")
        self.orderselect = QLineEdit("1")
        self.zselect = QLineEdit("1")
        self.offsetselect = QLineEdit("0.")
        self.avgwindowselect = QComboBox()


        """
        #NOTE:  This is formatted this way for easy reading
        settings = {}
        settings["autotrigger_on"]      = self.controlpanel.autotriggerselect.isChecked()
        settings["trigger_method"]      = self.controlpanel.trigger_methods[self.triggermethodselect.currentIndex()]
        settings["whittaker_lambda"]    = float(self.controlpanel.lambdaselect.text())
        settings["whittaker_order"]     = float(self.controlpanel.orderselect.text())
        settings["z"]                   = float(self.controlpanel.zselect.text())
        settings["manual_offset"]       = float(self.controlpanel.offsetselect.text())
        settings["averaging_window"]    = self.controlpanel.averaging_windows[self.avgwindowselect.currentIndex()]
        settings["polarity"]            = self.controlpanel.atpselect.currentIndex()
        settings["channel"]             = self.controlpanel.trigger_channel
        
        return settings