# This Python file uses the following encoding: utf-8
from PyQt6.QtCore import Qt, QThread
from PyQt6.QtWidgets import (QWidget, QGridLayout, QSizePolicy, QVBoxLayout, QHBoxLayout, 
        QPushButton, QSizePolicy, QCheckBox, QSpacerItem, QSplitter, QGroupBox, QLabel, QComboBox, 
        QDoubleSpinBox, QLineEdit, QProgressBar, QTextEdit)
import pyqtgraph as pg
import numpy as np
import time

try:
    from autotrigger_updater import AutotriggerUpdater
    from controlpanel_updater import ControlPanelUpdater
    from daq_updater import DaqUpdater
    from mainboard_updater import MainboardUpdater
except:
    from .autotrigger_updater import AutotriggerUpdater
    from .controlpanel_updater import ControlPanelUpdater
    from .daq_updater import DaqUpdater
    from .mainboard_updater import MainboardUpdater

"""!
@package Control Panel
This module includes the setup of the Control Panel tab and related object variables. 
"""

class ControlPanel(QWidget):
    """!
    Container widget for the control panel, the control panel contains all buttons needed for the 
    operation of the software.
    """

    def __init__(self, mainboard, controller, autotrigger):
        """!
        """
        super().__init__()
        
        self.controller = None
        self.mainboard = None
        self.autotrigger = None            
        
        self.ui_backend_thread = None
        self.mainboard_updater_thread = None
        self.daq_updater_thread = None
        self.autotrigger_updater_thread = None
        self.daq_connection = ""
        
        
        self.waveform_curves = []   #NOTE: See if we can change this to only be in the updater
        self.trigger_channel = 0
        
        self.dataCaptureSettings()
        self.analogTriggerSettings()
        self.autoTriggerSettings()
        self.timerSettings()
        self.laserSettings()
        self.filePlaybackSettings()
        self.oscilloscopeView()
        self.modeSelectionSettings()
        self.daqButtonsBox()
        self.terminalWindowBox()
        self.controllerSettingsBox()
        self.sensorSettings()
        self.createBaselineSmoothingBox()

        mainLayout = QGridLayout(self)

        mainLayout.addWidget(self.captureSettingsBox, 0, 0)
        mainLayout.addWidget(self.analogTriggerBox, 0, 1)
        mainLayout.addWidget(self.autoTriggerBox, 0, 2)
        mainLayout.addWidget(self.baselineSmoothingBox, 0, 3)
        mainLayout.addWidget(self.modeSelectionBox, 0, 4)
        mainLayout.addWidget(self.daqButtonsLayout, 0, 5)
        mainLayout.addWidget(self.timerSettingsBox, 1, 0)
        mainLayout.addWidget(self.laserSettingsBox, 1, 1)
        mainLayout.addWidget(self.controllerSettingsLayout, 1, 2, 1, 1)
        mainLayout.addWidget(self.sensorSettingsLayout, 1, 3, 1, 1)
        mainLayout.addWidget(self.filePlaybackBox, 1, 4, 1, 2)
        mainLayout.addWidget(self.oscilloscopeViewBox, 3, 0, 1, 4)
        mainLayout.addWidget(self.terminalLayout, 3, 4, 1, 1)
        
        mainLayout.setRowStretch(3,3)

        self.setupConnections(mainboard, controller, autotrigger)

        self.ui_backend.set_button_states()

        print("Control Panel UI Setup")

    def setupConnections(self, mainboard, controller, autotrigger):
        """
        This is the method that will be called to setup all connection information, and the ui
        backend will be setup for all options but the controlpanel_updater will enable/disable 
        buttons. 
        
        This will change slightly at a later date when everything is officially moved into the 
        kernel then the kernel will handle passing out the correct apis
        """
        self.mainboard_updater = MainboardUpdater(mainboard, self)
        self.mainboard_updater_thread = QThread()
        self.mainboard_updater.moveToThread(self.mainboard_updater_thread)

        self.autotrigger_updater = AutotriggerUpdater(autotrigger, self)
        self.autotrigger_updater_thread = QThread()
        self.autotrigger_updater.moveToThread(self.autotrigger_updater_thread)

        self.daq_updater = DaqUpdater(controller, self)
        self.daq_updater_thread = QThread()
        self.daq_updater.moveToThread(self.daq_updater_thread)
        
        self.ui_backend = ControlPanelUpdater(controller, self)
        self.ui_backend_thread = QThread()
        self.ui_backend.moveToThread(self.ui_backend_thread)

    def finish(self):
        #TODO:  clean up all running threads and everything else
        if self.ui_backend_thread:
            self.ui_backend_thread.quit()
        if self.autotrigger_updater_thread:
            self.autotrigger_updater_thread.quit()
        if self.daq_updater_thread:
            self.daq_updater_thread.quit()
        if self.mainboard_updater_thread:
            self.mainboard_updater_thread.quit()
        print("Control Panel UI backend quit")
            
    def dataCaptureSettings(self):
        """!
        This method is called to create all items in the top left box (Data Capture Settings)
        
        Assigns:
            topLeftGroupBox
            daqcapturelengthselect
            daqcaptureoffselect
        
        Inputs: None
        Outputs: None
        """
        self.captureSettingsBox = QGroupBox("Data Capture Settings")

        hsplitter1 = QSplitter(Qt.Orientation.Horizontal, self)
        modetitle = QLabel("Mode")
        self.daqcapturemodeselect = QComboBox()
        self.daqcapturemodeselect.addItem("None")
        self.daqcapturemodeselect.addItem("Free-Run")
        self.daqcapturemodeselect.addItem("External Trigger")
        self.daqcapturemodeselect.addItem("Analog Trigger")
        self.daqcapturemodeselect.setCurrentIndex(0)
        hsplitter1.addWidget(modetitle)
        hsplitter1.addWidget(self.daqcapturemodeselect)

        hsplitter2 = QSplitter(Qt.Orientation.Horizontal, self)
        cltitle = QLabel("Capture Length")
        self.daqcapturelengthselect = QComboBox()
        self.daqcapturelengthselect.addItem("2us")
        self.daqcapturelengthselect.addItem("5us")
        self.daqcapturelengthselect.addItem("10us")
        self.daqcapturelengthselect.addItem("20us")
        self.daqcapturelengthselect.addItem("50us")
        self.daqcapturelengthselect.addItem("75us")
        self.daqcapturelengthselect.addItem("100us")
        self.daqcapturelengthselect.addItem("130us")
        self.daqcapturelengthselect.setCurrentIndex(4)
        hsplitter2.addWidget(cltitle)
        hsplitter2.addWidget(self.daqcapturelengthselect)

        hsplitter3 = QSplitter(Qt.Orientation.Horizontal, self)
        cotitle = QLabel("Capture Offset")
        self.daqcaptureoffsetselect = QComboBox()
        self.daqcaptureoffsetselect.addItem("16ns")
        self.daqcaptureoffsetselect.addItem("1us")
        self.daqcaptureoffsetselect.addItem("2us")
        self.daqcaptureoffsetselect.addItem("5us")
        self.daqcaptureoffsetselect.addItem("10us")
        self.daqcaptureoffsetselect.addItem("20us")
        self.daqcaptureoffsetselect.addItem("25us")
        self.daqcaptureoffsetselect.addItem("30us")
        self.daqcaptureoffsetselect.setCurrentIndex(0)
        hsplitter3.addWidget(cotitle)
        hsplitter3.addWidget(self.daqcaptureoffsetselect)

        layout = QVBoxLayout()
        layout.addWidget(hsplitter1)
        layout.addWidget(hsplitter2)
        layout.addWidget(hsplitter3)

        self.captureSettingsBox.setLayout(layout)

    def analogTriggerSettings(self):
        """!
        This method is called to create all items in the middle left box (Analog Trigger Settings)
        
        Assigns:
            middleLeftGroupBox
            atcselect
            atpselect
            athreshselect
            ahystselect
        
        Inputs: None
        Outputs: None
        """
        self.analogTriggerBox = QGroupBox("Analog Trigger Settings")

        hsplitter4 = QSplitter(Qt.Orientation.Horizontal, self)
        atctitle = QLabel("Channel")
        self.atcdselect = QComboBox()
        self.atcdselect.addItem("DAQ 0")
        self.atcdselect.addItem("DAQ 1")
        self.atcdselect.addItem("DAQ 2")
        self.atcdselect.addItem("DAQ 3")
        self.atcdselect.addItem("None")
        self.atcdselect.setCurrentIndex(4)
        self.atccselect = QDoubleSpinBox()
        self.atccselect.setKeyboardTracking(False)
        self.atccselect.setDecimals(0)
        self.atccselect.setRange(0,11)
        self.atccselect.setSingleStep(1)
        self.atccselect.setValue(0)
        hsplitter4.addWidget(atctitle)
        hsplitter4.addWidget(self.atcdselect)
        hsplitter4.addWidget(self.atccselect)

        hsplitter1 = QSplitter(Qt.Orientation.Horizontal, self)
        atptitle = QLabel("Polarity")
        self.atpselect = QComboBox()
        self.atpselect.addItem("Falling")
        self.atpselect.addItem("Rising")
        hsplitter1.addWidget(atptitle)
        hsplitter1.addWidget(self.atpselect)

        hsplitter2 = QSplitter(Qt.Orientation.Horizontal, self)
        athreshtitle = QLabel("Threshold")
        self.athreshselect = QDoubleSpinBox()
        self.athreshselect.setKeyboardTracking(False)
        self.athreshselect.setDecimals(3)
        self.athreshselect.setRange(-0.900000000000000,0.900000000000000)
        self.athreshselect.setSingleStep(0.001000000000000)
        self.athreshselect.setValue(0.00000000000000)
        hsplitter2.addWidget(athreshtitle)
        hsplitter2.addWidget(self.athreshselect)

        hsplitter3 = QSplitter(Qt.Orientation.Horizontal, self)
        ahysttitle = QLabel("Hysteresis")
        self.ahystselect = QDoubleSpinBox()
        self.ahystselect.setKeyboardTracking(False)
        self.ahystselect.setDecimals(3)
        self.ahystselect.setRange(0.000000000000000, 0.099000000000000)
        self.ahystselect.setSingleStep(0.001000000000000)
        self.ahystselect.setValue(0.000000000000001)
        hsplitter3.addWidget(ahysttitle)
        hsplitter3.addWidget(self.ahystselect)

        layout = QVBoxLayout()
        layout.addWidget(hsplitter4)
        layout.addWidget(hsplitter1)
        layout.addWidget(hsplitter2)
        layout.addWidget(hsplitter3)

        self.analogTriggerBox.setLayout(layout)

    def autoTriggerSettings(self):
        """!
        This method is called to create all items in the middle left box (Automated DAQ Trigger Settings)
        
        Assigns:
        
        Inputs: None
        Outputs: None
        
        "trigger_method":"smoothed",
        "whittaker_lambda": 10,
        "whittaker_order": 1,
        "sigma_z": 1.4,
        "manual_offset": 0.,
        "averaging_window": 5,
        "signal_type": "falling"

        """

        self.averaging_windows = {0:'5', 1:'10',2:'20',3:'50',4:'100'}
        self.trigger_methods = {0:'simple',
                                1: 'smoothed'}


        self.autoTriggerBox = QGroupBox("Automated Trigger Settings")

        hsplitter1 = QSplitter(Qt.Orientation.Horizontal, self)
        autotriggertitle = QLabel("Autotrigger")
        self.autotriggerselect = QCheckBox()
        hsplitter1.addWidget(autotriggertitle)
        hsplitter1.addWidget(self.autotriggerselect)

        hsplitter2 = QSplitter(Qt.Orientation.Horizontal, self)
        triggermethodtitle = QLabel("Trigger Method")
        triggermethodtitle.setToolTip("Simple: Standard baseline subtraction\nSmoothed: Whittaker-Eiler smoothing (recommended)")
        self.triggermethodselect = QComboBox()
        for k, v in self.trigger_methods.items():
            self.triggermethodselect.addItem(v)
        hsplitter2.addWidget(triggermethodtitle)
        hsplitter2.addWidget(self.triggermethodselect)

        hsplitter3 = QSplitter(Qt.Orientation.Horizontal, self)
        lambdatitle = QLabel("lambda")
        lambdatitle.setToolTip("This is the weighting of the deviation between the baseline and the estimated value (values can be 100-1000)")
        self.lambdaselect = QLineEdit("10")
        self.lambdaselect.setFixedSize(80,20)
        hsplitter3.addWidget(lambdatitle)
        hsplitter3.addWidget(self.lambdaselect)

        hsplitter4 = QSplitter(Qt.Orientation.Horizontal, self)
        ordertitle = QLabel("order")
        ordertitle.setToolTip("This is the weighting of the deviance (values can be 1-5 (best are 1-3))")
        self.orderselect = QLineEdit("1")
        self.orderselect.setFixedSize(80,20)
        hsplitter4.addWidget(ordertitle)
        hsplitter4.addWidget(self.orderselect)

        hsplitter5 = QSplitter(Qt.Orientation.Horizontal, self)
        ztitle = QLabel("z")
        ztitle.setToolTip("This is the weighting of the baseline subtraction")
        self.zselect = QLineEdit("1")
        self.zselect.setFixedSize(80,20)
        hsplitter5.addWidget(ztitle)
        hsplitter5.addWidget(self.zselect)

        hsplitter6 = QSplitter(Qt.Orientation.Horizontal, self)
        manualoffsettitle = QLabel("manual offset")
        manualoffsettitle.setToolTip("This is a manual tweak to set the trigger line either higher or lower given the value (need to have +/-)")
        self.offsetselect = QLineEdit("0.")
        self.offsetselect.setFixedSize(80,20)
        hsplitter6.addWidget(manualoffsettitle)
        hsplitter6.addWidget(self.offsetselect)

        hsplitter7 = QSplitter(Qt.Orientation.Horizontal, self)
        averagingwindowtitle = QLabel("averaging window")
        averagingwindowtitle.setToolTip("This is the number of events that get averaged into the baseline (lower number means quicker averaging (10-20 is typical))")
        self.avgwindowselect = QComboBox()
        for k, v in self.averaging_windows.items():
            self.avgwindowselect.addItem(v)
        hsplitter7.addWidget(averagingwindowtitle)
        hsplitter7.addWidget(self.avgwindowselect)        


        layout = QVBoxLayout()
        layout.addWidget(hsplitter1)
        layout.addWidget(hsplitter2)
        layout.addWidget(hsplitter3)
        layout.addWidget(hsplitter4)
        layout.addWidget(hsplitter5)
        layout.addWidget(hsplitter6)
        layout.addWidget(hsplitter7)

        self.autoTriggerBox.setLayout(layout)

    def daqButtonsBox(self):
        self.daqButtonsLayout = QGroupBox("DAQ Buttons")

        self.nop = QPushButton("Send NOP")
        self.nop.setFixedSize(100, 50)

        self.daq_ver_info = QPushButton("Request Version")
        self.daq_ver_info.setFixedSize(100, 50)

        self.daq_settings = QPushButton("Request Settings")
        self.daq_settings.setFixedSize(100, 50)

        #NOTE:  This might be able to be removed if we just set everything to emit a signal
        self.daq_apply = QPushButton("Apply Settings")
        self.daq_apply.setFixedSize(100, 50)

        layout = QGridLayout()
        layout.addWidget(self.nop, 0, 0)
        layout.addWidget(self.daq_ver_info, 0, 1)
        layout.addWidget(self.daq_settings, 1, 0)
        layout.addWidget(self.daq_apply, 1, 1)

        self.daqButtonsLayout.setLayout(layout)        

    def timerSettings(self):
        """!
        This method is called to create all items for the bottomLeftGroupBox (Time Settings)
        
        Assigns:
        
        Inputs: None
        Outputs: None
        """
        self.timerSettingsBox = QGroupBox("Timer Settings")

        hsplitter1 = QSplitter(Qt.Orientation.Horizontal, self)
        pulsetitle = QLabel("Pulse")
        self.pulse_setting = QDoubleSpinBox()
        self.pulse_setting.setKeyboardTracking(False)
        self.pulse_setting.setDecimals(0)
        self.pulse_setting.setRange(0,7)
        self.pulse_setting.setSingleStep(1)
        self.pulse_setting.setValue(0)
        hsplitter1.addWidget(pulsetitle)
        hsplitter1.addWidget(self.pulse_setting)

        hsplitter2 = QSplitter(Qt.Orientation.Horizontal, self)
        delaytitle = QLabel("Initial Delay")
        self.delay_setting = QDoubleSpinBox()
        self.delay_setting.setKeyboardTracking(False)
        self.delay_setting.setDecimals(0)
        self.delay_setting.setRange(0,65535)
        self.delay_setting.setSingleStep(1)
        self.delay_setting.setValue(10)
        hsplitter2.addWidget(delaytitle)
        hsplitter2.addWidget(self.delay_setting)

        hsplitter3 = QSplitter(Qt.Orientation.Horizontal, self)
        ontitle = QLabel("ON Time")
        self.on_time_setting = QDoubleSpinBox()
        self.on_time_setting.setKeyboardTracking(False)
        self.on_time_setting.setDecimals(0)
        self.on_time_setting.setRange(0,65535)
        self.on_time_setting.setSingleStep(1)
        self.on_time_setting.setValue(10)
        hsplitter3.addWidget(ontitle)
        hsplitter3.addWidget(self.on_time_setting)

        hsplitter4 = QSplitter(Qt.Orientation.Horizontal, self)
        offtitle = QLabel("OFF Time")
        self.off_time_setting = QDoubleSpinBox()
        self.off_time_setting.setKeyboardTracking(False)
        self.off_time_setting.setDecimals(0)
        self.off_time_setting.setRange(0,65535)
        self.off_time_setting.setSingleStep(1)
        self.off_time_setting.setValue(10)
        hsplitter4.addWidget(offtitle)
        hsplitter4.addWidget(self.off_time_setting)

        layout = QVBoxLayout()
        layout.addWidget(hsplitter1)
        layout.addWidget(hsplitter2)
        layout.addWidget(hsplitter3)
        layout.addWidget(hsplitter4)
        # layout.addStretch(1)
        self.timerSettingsBox.setLayout(layout)

    def modeSelectionSettings(self):
        """!
        This method is called to create all items for the bottom left buttons (Mode Selection)
        
        Assigns:
            bottomLeftButtonsGroupBox
            daq_button
            player_button
        
        Inputs: None
        Outputs: None
        """
        self.modeSelectionBox = QGroupBox("Mode Selection")
        #NOTE:  At this time in the ssm-kernel it does nothing
        self.database_button = QPushButton("Clear DB")
        self.database_button.setFixedSize(100, 50)

        self.player_button = QPushButton("Player")
        self.player_button.setFixedSize(100, 50)
        
        #NOTE:  At this time in the ssm-kernel it does nothing
        self.database_connection_button = QPushButton("Connect DB")
        self.database_connection_button.setFixedSize(100,50)

        buttonLayout = QHBoxLayout()
        buttonLayout2 = QHBoxLayout()
        verticalLayout = QVBoxLayout()
        buttonLayout.addWidget(self.database_button)
        buttonLayout.addWidget(self.player_button)
        buttonLayout2.addWidget(self.database_connection_button)
        
        verticalLayout.addLayout(buttonLayout)
        verticalLayout.addLayout(buttonLayout2)

        self.modeSelectionBox.setLayout(verticalLayout)

    def createBaselineSmoothingBox(self):
        self.baselineSmoothingBox = QGroupBox("Baseline Smoothing")

        daq0Enable = QLabel('DAQ 0')
        self.daq0Math = QCheckBox()
        daq1Enable = QLabel('DAQ 1')
        self.daq1Math = QCheckBox()
        daq2Enable = QLabel('DAQ 2')
        self.daq2Math = QCheckBox()
        daq3Enable = QLabel('DAQ 3')
        self.daq3Math = QCheckBox()
        
        polarityTitle = QLabel('Polarity')
        polarityTitle.setToolTip('Set the polarity of the smoothing either (Falling or Rising)')
        self.baseline_polarity = QComboBox()
        self.baseline_polarity.addItem('Falling')
        self.baseline_polarity.addItem('Positive')
        
        smoothingTitle = QLabel('Smoothing (samples)')
        smoothingTitle.setToolTip('Select the number of samples to smooth over (also referred to as Smoothing Window)')
        self.baseline_smoothing = QComboBox()
        self.baseline_smoothing.addItem('8')
        self.baseline_smoothing.addItem('16')
        self.baseline_smoothing.addItem('32')
        self.baseline_smoothing.addItem('64')
        self.baseline_smoothing.addItem('128')
        self.baseline_smoothing.addItem('256')
        self.baseline_smoothing.addItem('512')
        self.baseline_smoothing.addItem('1024')
        
        slewrateTitle = QLabel('Slew Rate (uV)')
        slewrateTitle.setToolTip('Select the slew rate to use in the smoothign function (in micro Volts)')
        self.baseline_slew_rate = QComboBox()
        self.baseline_slew_rate.addItem('0.3125')
        self.baseline_slew_rate.addItem('0.625')
        self.baseline_slew_rate.addItem('1.25')
        self.baseline_slew_rate.addItem('2.5')
        self.baseline_slew_rate.addItem('5.0')
        self.baseline_slew_rate.addItem('10.0')
        self.baseline_slew_rate.addItem('20.0')
        self.baseline_slew_rate.addItem('40.0')
        
        horLayout = QHBoxLayout()
        vertLayout1 = QVBoxLayout()
        vertLayout2 = QVBoxLayout()
        
        vertLayout1.addWidget(daq0Enable)
        vertLayout1.addWidget(daq1Enable)
        vertLayout1.addWidget(daq2Enable)
        vertLayout1.addWidget(daq3Enable)
        vertLayout1.addWidget(polarityTitle)
        vertLayout1.addWidget(smoothingTitle)
        vertLayout1.addWidget(slewrateTitle)
        
        vertLayout2.addWidget(self.daq0Math)
        vertLayout2.addWidget(self.daq1Math)
        vertLayout2.addWidget(self.daq2Math)
        vertLayout2.addWidget(self.daq3Math)
        vertLayout2.addWidget(self.baseline_polarity)
        vertLayout2.addWidget(self.baseline_smoothing)
        vertLayout2.addWidget(self.baseline_slew_rate)
        
        horLayout.addLayout(vertLayout1)
        horLayout.addLayout(vertLayout2)    
        
        self.baselineSmoothingBox.setLayout(horLayout)

    def laserSettings(self):
        """!
        This method is called to create all the items for the top right box (Laser Timing) 
        
        Assigns:
            topRightGroupBox
            laserpulsewindowselect
            laserpulsedelayselect
        
        Inputs: None
        Outputs: None
        """
        self.laserSettingsBox = QGroupBox("Laser Settings")

        hsplitter0 = QSplitter(Qt.Orientation.Horizontal, self)
        self.laser_status = QProgressBar()
        self.laser_status.setFormat("Lasers")
        self.laser_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.laser_status.setValue(100)
        self.laser_status.setStyleSheet("QProgressBar::chunk {background-color: red;}")
        self.laser_status.setMaximumWidth(40)
        modetitle = QLabel("Mode")
        seqtitle = QLabel("Sequence")
        powertitle = QLabel("Power")
        tectitle = QLabel("TEC")
        hsplitter0.addWidget(self.laser_status)
        hsplitter0.addWidget(modetitle)
        hsplitter0.addWidget(seqtitle)
        hsplitter0.addWidget(powertitle)
        hsplitter0.addWidget(tectitle)

        self.laser_mode = []
        self.laser_seq = []
        self.laser_power = []
        self.laser_tec = []

        hsplitter1 = QSplitter(Qt.Orientation.Horizontal, self)
        las0title = QLabel("Laser 0")
        laser_0_mode = QComboBox()
        laser_0_mode.addItem("Off")
        laser_0_mode.addItem("On")
        laser_0_mode.addItem("Timed")
        laser_0_seq = QDoubleSpinBox()
        laser_0_seq.setKeyboardTracking(False)
        laser_0_seq.setDecimals(0)
        laser_0_seq.setRange(0,7)
        laser_0_seq.setSingleStep(1)
        laser_0_seq.setValue(0)
        laser_0_power = QDoubleSpinBox()
        laser_0_power.setKeyboardTracking(False)
        laser_0_power.setDecimals(2)
        laser_0_power.setRange(10,100)
        laser_0_power.setSingleStep(1)
        laser_0_power.setValue(10)
        laser_0_tec = QCheckBox()
        hsplitter1.addWidget(las0title)
        hsplitter1.addWidget(laser_0_mode)
        hsplitter1.addWidget(laser_0_seq)
        hsplitter1.addWidget(laser_0_power)
        hsplitter1.addWidget(laser_0_tec)
        self.laser_mode.append(laser_0_mode)
        self.laser_seq.append(laser_0_seq)
        self.laser_power.append(laser_0_power)
        self.laser_tec.append(laser_0_tec)

        hsplitter2 = QSplitter(Qt.Orientation.Horizontal, self)
        las1title = QLabel("Laser 1")
        laser_1_mode = QComboBox()
        laser_1_mode.addItem("Off")
        laser_1_mode.addItem("On")
        laser_1_mode.addItem("Timed")
        laser_1_seq = QDoubleSpinBox()
        laser_1_seq.setKeyboardTracking(False)
        laser_1_seq.setDecimals(0)
        laser_1_seq.setRange(0,7)
        laser_1_seq.setSingleStep(1)
        laser_1_seq.setValue(0)
        laser_1_power = QDoubleSpinBox()
        laser_1_power.setKeyboardTracking(False)
        laser_1_power.setDecimals(2)
        laser_1_power.setRange(10,100)
        laser_1_power.setSingleStep(1)
        laser_1_power.setValue(10)
        laser_1_tec = QCheckBox()
        hsplitter2.addWidget(las1title)
        hsplitter2.addWidget(laser_1_mode)
        hsplitter2.addWidget(laser_1_seq)
        hsplitter2.addWidget(laser_1_power)
        hsplitter2.addWidget(laser_1_tec)
        self.laser_mode.append(laser_1_mode)
        self.laser_seq.append(laser_1_seq)
        self.laser_power.append(laser_1_power)
        self.laser_tec.append(laser_1_tec)

        hsplitter3 = QSplitter(Qt.Orientation.Horizontal, self)
        las2title = QLabel("Laser 2")
        laser_2_mode = QComboBox()
        laser_2_mode.addItem("Off")
        laser_2_mode.addItem("On")
        laser_2_mode.addItem("Timed")
        laser_2_seq = QDoubleSpinBox()
        laser_2_seq.setKeyboardTracking(False)
        laser_2_seq.setDecimals(0)
        laser_2_seq.setRange(0,7)
        laser_2_seq.setSingleStep(1)
        laser_2_seq.setValue(0)
        laser_2_power = QDoubleSpinBox()
        laser_2_power.setKeyboardTracking(False)
        laser_2_power.setDecimals(2)
        laser_2_power.setRange(10,100)
        laser_2_power.setSingleStep(1)
        laser_2_power.setValue(10)
        laser_2_tec = QCheckBox()
        hsplitter3.addWidget(las2title)
        hsplitter3.addWidget(laser_2_mode)
        hsplitter3.addWidget(laser_2_seq)
        hsplitter3.addWidget(laser_2_power)
        hsplitter3.addWidget(laser_2_tec)
        self.laser_mode.append(laser_2_mode)
        self.laser_seq.append(laser_2_seq)
        self.laser_power.append(laser_2_power)
        self.laser_tec.append(laser_2_tec)

        hsplitter4 = QSplitter(Qt.Orientation.Horizontal, self)
        las3title = QLabel("Laser 3")
        laser_3_mode = QComboBox()
        laser_3_mode.addItem("Off")
        laser_3_mode.addItem("On")
        laser_3_mode.addItem("Timed")
        laser_3_seq = QDoubleSpinBox()
        laser_3_seq.setKeyboardTracking(False)
        laser_3_seq.setDecimals(0)
        laser_3_seq.setRange(0,7)
        laser_3_seq.setSingleStep(1)
        laser_3_seq.setValue(0)
        laser_3_power = QDoubleSpinBox()
        laser_3_power.setKeyboardTracking(False)
        laser_3_power.setDecimals(2)
        laser_3_power.setRange(10,100)
        laser_3_power.setSingleStep(1)
        laser_3_power.setValue(10)
        laser_3_tec = QCheckBox()
        hsplitter4.addWidget(las3title)
        hsplitter4.addWidget(laser_3_mode)
        hsplitter4.addWidget(laser_3_seq)
        hsplitter4.addWidget(laser_3_power)
        hsplitter4.addWidget(laser_3_tec)
        self.laser_mode.append(laser_3_mode)
        self.laser_seq.append(laser_3_seq)
        self.laser_power.append(laser_3_power)
        self.laser_tec.append(laser_3_tec)

        hsplitter5 = QSplitter(Qt.Orientation.Horizontal, self)
        las4title = QLabel("Laser 4")
        laser_4_mode = QComboBox()
        laser_4_mode.addItem("Off")
        laser_4_mode.addItem("On")
        laser_4_mode.addItem("Timed")
        laser_4_seq = QDoubleSpinBox()
        laser_4_seq.setKeyboardTracking(False)
        laser_4_seq.setDecimals(0)
        laser_4_seq.setRange(0,7)
        laser_4_seq.setSingleStep(1)
        laser_4_seq.setValue(0)
        laser_4_power = QDoubleSpinBox()
        laser_4_power.setKeyboardTracking(False)
        laser_4_power.setDecimals(2)
        laser_4_power.setRange(10,100)
        laser_4_power.setSingleStep(1)
        laser_4_power.setValue(10)
        laser_4_tec = QCheckBox()
        hsplitter5.addWidget(las4title)
        hsplitter5.addWidget(laser_4_mode)
        hsplitter5.addWidget(laser_4_seq)
        hsplitter5.addWidget(laser_4_power)
        hsplitter5.addWidget(laser_4_tec)
        self.laser_mode.append(laser_4_mode)
        self.laser_seq.append(laser_4_seq)
        self.laser_power.append(laser_4_power)
        self.laser_tec.append(laser_4_tec)

        hsplitter6 = QSplitter(Qt.Orientation.Horizontal, self)
        las5title = QLabel("Laser 5")
        laser_5_mode = QComboBox()
        laser_5_mode.addItem("Off")
        laser_5_mode.addItem("On")
        laser_5_mode.addItem("Timed")
        laser_5_seq = QDoubleSpinBox()
        laser_5_seq.setKeyboardTracking(False)
        laser_5_seq.setDecimals(0)
        laser_5_seq.setRange(0,7)
        laser_5_seq.setSingleStep(1)
        laser_5_seq.setValue(0)
        laser_5_power = QDoubleSpinBox()
        laser_0_power.setKeyboardTracking(False)
        laser_5_power.setDecimals(2)
        laser_5_power.setRange(10,100)
        laser_5_power.setSingleStep(1)
        laser_5_power.setValue(10)
        laser_5_tec = QCheckBox()
        hsplitter6.addWidget(las5title)
        hsplitter6.addWidget(laser_5_mode)
        hsplitter6.addWidget(laser_5_seq)
        hsplitter6.addWidget(laser_5_power)
        hsplitter6.addWidget(laser_5_tec)
        self.laser_mode.append(laser_5_mode)
        self.laser_seq.append(laser_5_seq)
        self.laser_power.append(laser_5_power)
        self.laser_tec.append(laser_5_tec)

        layout = QVBoxLayout()
        layout.addWidget(hsplitter0)
        layout.addWidget(hsplitter1)
        layout.addWidget(hsplitter2)
        layout.addWidget(hsplitter3)
        layout.addWidget(hsplitter4)
        layout.addWidget(hsplitter5)
        layout.addWidget(hsplitter6)
        self.laserSettingsBox.setLayout(layout)

    def filePlaybackSettings(self):
        """!
        This method is called to create all items in the middle right box (File Playback)
        
        Assigns:
            play_button
            stop_button
            pause_button
            rewind_buton
            load_button
            capture_button
            frame_num_label
            frame_total_label
            filename_label
        
        Inputs: None
        Outputs: None
        """
        self.filePlaybackBox = QGroupBox("File Playback")

        self.play_button = QPushButton("Play")
        self.play_button.setFixedSize(100, 100)
        self.play_button.setEnabled(False)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setFixedSize(100, 100)

        self.pause_button = QPushButton("Pause")
        self.pause_button.setFixedSize(100, 100)

        self.rewind_button = QPushButton("Rewind")
        self.rewind_button.setFixedSize(100, 100)

        self.fastforward_button = QPushButton("Fast Forward")
        self.fastforward_button.setFixedSize(100, 100)

        self.seek_button = QPushButton("Seek")
        self.seek_button.setFixedSize(100, 100)

        self.load_button = QPushButton("Load")
        self.load_button.setFixedSize(100, 100)

        self.capture_button = QPushButton("Record")
        self.capture_button.setFixedSize(100, 100)

        self.frame_num_label = QLineEdit("0")
        self.frame_num_label.setFixedSize(150,20)
        self.frame_total_label = QLineEdit(f"0")
        self.frame_total_label.setEnabled(False)
        self.frame_total_label.setFixedSize(150,20)

        self.filename_label = QLineEdit("")

        buttonLayout = QHBoxLayout()
        buttonLayout.addItem(QSpacerItem(50, 100, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed))
        buttonLayout.addWidget(self.play_button)
        buttonLayout.addWidget(self.stop_button)
        buttonLayout.addWidget(self.pause_button)
        buttonLayout.addWidget(self.rewind_button)
        buttonLayout.addWidget(self.fastforward_button)
        buttonLayout.addWidget(self.seek_button)
        buttonLayout.addWidget(self.load_button)
        buttonLayout.addWidget(self.capture_button)
        buttonLayout.addItem(QSpacerItem(50, 100, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed))

        button_widget = QWidget()
        button_widget.setLayout(buttonLayout)

        labelLayout = QHBoxLayout()

        labelLayout.addWidget(self.frame_num_label)
        labelLayout.addWidget(self.frame_total_label)
        labelLayout.addWidget(self.filename_label)

        label_widget = QWidget()
        label_widget.setLayout(labelLayout)

        vsplitter = QSplitter(Qt.Orientation.Vertical, self)
        vsplitter.addWidget(button_widget)
        vsplitter.addWidget(label_widget)

        total_layout = QHBoxLayout()
        total_layout.addWidget(vsplitter)

        self.filePlaybackBox.setLayout(total_layout)

    def oscilloscopeView(self):
        """!
        This method is called to create all of the items in the BottomRightBox (Oscilloscope
        Parameters)
        
        Assigns:
            bottomRightGroupBox
            athresh
            hthresh
            oscilloscope
        
        Inputs: None
        Outputs: None
        """
        self.oscilloscopeViewBox = QGroupBox("Oscilloscope Parameters")

        horizontalLayout = QHBoxLayout()

        #NOTE: This will be an attempt to change the oscilloscope view to only the trigger signal
        self.oscilloscope = pg.PlotWidget()
        self.oscilloscope.getPlotItem().getViewBox().disableAutoRange(axis='y')
        self.oscilloscope.getPlotItem().getViewBox().setYRange(-1.1, 1.1)
        self.oscilloscope.getPlotItem().getViewBox().setXRange(0, 2500)
        self.oscilloscope.setBackground('w')
        self.oscilloscope.showGrid(x=True, y=True)
        self.oscilloscope.setLabel('left', "ADC of Trigger Channel")
        self.oscilloscope.setMenuEnabled(False)

        pen = pg.mkPen('g', width=1)
        self.thresh_line = pg.InfiniteLine(pos=0, movable=False, angle=0, pen=pen )
        pen = pg.mkPen('r', width=1)
        self.hyst_line_top = pg.InfiniteLine(pos=0, movable=False, angle=0, pen=pen)
        pen = pg.mkPen('r', width=1)
        self.hyst_line_bot = pg.InfiniteLine(pos=0, movable=False, angle=0, pen=pen)
        
        self.oscilloscope.addItem(self.hyst_line_top, ignoreBounds=True)
        self.oscilloscope.addItem(self.hyst_line_bot, ignoreBounds=True)
        self.oscilloscope.addItem(self.thresh_line, ignoreBounds=True)
        self.waveform_curves = self.oscilloscope.plot(pen=pg.mkPen('b'))

        horizontalLayout.addWidget(self.oscilloscope)

        self.oscilloscopeViewBox.setLayout(horizontalLayout)

    def terminalWindowBox(self):
        self.terminalLayout = QGroupBox("Mainboard Communication")

        hsplitter1 = QSplitter(Qt.Orientation.Horizontal, self)
        self.com_port_edit = QLineEdit()
        self.com_port_edit.setPlaceholderText("COM Port")
        self.com_port_edit.setFixedSize(200,35)
        self.com_port_connect = QPushButton("Connect")
        self.com_port_connect.setFixedSize(100,35)
        self.com_port_connect.setToolTip("This button connects the communication path\nbetween the software and the mainboard")
        self.daq_turn_on = QPushButton("Connect DAQ")
        self.daq_turn_on.setFixedSize(100,35)
        
        #TODO:  Make sure that connect daqs works once the mainboard has been connected
        if self.daq_connection == "":
            self.daq_turn_on.setEnabled(False)
            self.daq_turn_on.setToolTip("This button is disabled for only running the Control Panel")
        else:
            self.daq_turn_on.setToolTip("This button opens the communication path way\nbetween the software and the DAQ boards")
        self.daq_connection = "Player"
        self.daqs_connected = QLabel("")
        
        hsplitter1.addWidget(self.com_port_edit)
        hsplitter1.addWidget(self.com_port_connect)
        hsplitter1.addWidget(self.daq_turn_on)
        hsplitter1.addWidget(self.daqs_connected)

        self.terminal_out = QTextEdit()

        self.discard_report = QCheckBox("Discard Status Report")

        layout = QVBoxLayout()
        layout.addWidget(hsplitter1)
        layout.addWidget(self.terminal_out)
        layout.addWidget(self.discard_report)

        self.terminalLayout.setLayout(layout)

    def controllerSettingsBox(self):
        self.controllerSettingsLayout = QGroupBox("Controller Settings")

        hsplitter1 = QSplitter(Qt.Orientation.Horizontal, self)
        statustitle = QLabel("Status Period")
        self.status_period = QDoubleSpinBox()
        self.status_period.setKeyboardTracking(False)
        self.status_period.setDecimals(0)
        self.status_period.setRange(0,10000)
        self.status_period.setSingleStep(1)
        self.status_period.setValue(0)
        statusunit = QLabel("ms")
        hsplitter1.addWidget(statustitle)
        hsplitter1.addWidget(self.status_period)
        hsplitter1.addWidget(statusunit)

        hsplitter2 = QSplitter(Qt.Orientation.Horizontal, self)
        tracetitle = QLabel("Trace Level")
        self.trace_level = QDoubleSpinBox()
        self.trace_level.setKeyboardTracking(False)
        self.trace_level.setDecimals(0)
        self.trace_level.setRange(0,3)
        self.trace_level.setSingleStep(1)
        self.trace_level.setValue(0)
        hsplitter2.addWidget(tracetitle)
        hsplitter2.addWidget(self.trace_level)

        checkboxes = QGridLayout()
        moduletitle = QLabel("Module Enable")
        self.daq_0 = QCheckBox("DAQ [0]")
        self.daq_1 = QCheckBox("DAQ [1]")
        self.daq_2 = QCheckBox("DAQ [2]")
        self.daq_3 = QCheckBox("DAQ [3]")
        self.las_4 = QCheckBox("LAS [4]")
        self.sif_5 = QCheckBox("SIF [5]")
        self.flc_6 = QCheckBox("FLC [6]")
        self.extra_7 = QCheckBox("[7]")
        checkboxes.addWidget(moduletitle, 0, 0)
        checkboxes.addWidget(self.daq_0, 0, 1)
        checkboxes.addWidget(self.daq_1, 1, 1)
        checkboxes.addWidget(self.daq_2, 2, 1)
        checkboxes.addWidget(self.daq_3, 3, 1)
        checkboxes.addWidget(self.las_4, 0, 2)
        checkboxes.addWidget(self.sif_5, 1, 2)
        checkboxes.addWidget(self.flc_6, 2, 2)
        checkboxes.addWidget(self.extra_7, 3, 2)    

        layout = QVBoxLayout()
        layout.addWidget(hsplitter1)
        layout.addWidget(hsplitter2)
        layout.addLayout(checkboxes)

        self.controllerSettingsLayout.setLayout(layout)

    def sensorSettings(self):
        self.sensorSettingsLayout = QGroupBox("Sensor Settings")

        self.sensor_status = QProgressBar()
        self.sensor_status.setFormat("Sensors")
        self.sensor_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sensor_status.setValue(100)
        self.sensor_status.setStyleSheet("QProgressBar::chunk {background-color: red;}")
        self.sensor_status.setMaximumWidth(40)

        hsplitter1 = QSplitter(Qt.Orientation.Horizontal, self)
        voltagetitle = QLabel("Voltage")
        self.voltage_value = QDoubleSpinBox()
        self.voltage_value.setKeyboardTracking(False)
        self.voltage_value.setDecimals(2)
        self.voltage_value.setRange(0,29)
        self.voltage_value.setSingleStep(1)
        self.voltage_value.setValue(26)
        hsplitter1.addWidget(voltagetitle)
        hsplitter1.addWidget(self.voltage_value)

        hsplitter2 = QSplitter(Qt.Orientation.Horizontal, self)
        modetitle = QLabel("TEC Mode")
        self.tec_settings = QComboBox()
        self.tec_settings.addItem("Auto (-30C)")
        self.tec_settings.addItem("Constant Tempurature")
        self.tec_settings.addItem("Constant Voltage")
        self.tec_settings.setCurrentIndex(2)
        hsplitter2.addWidget(modetitle)
        hsplitter2.addWidget(self.tec_settings)

        hsplitter3 = QSplitter(Qt.Orientation.Horizontal, self)
        temptitle = QLabel("TEC Tempurature")
        self.temp_value = QDoubleSpinBox()
        self.temp_value.setKeyboardTracking(False)
        self.temp_value.setDecimals(2)
        self.temp_value.setRange(-35,0)
        self.temp_value.setSingleStep(1)
        self.temp_value.setValue(-30)
        hsplitter3.addWidget(temptitle)
        hsplitter3.addWidget(self.temp_value)

        hsplitter4 = QSplitter(Qt.Orientation.Horizontal, self)
        tecvoltagetitle = QLabel("TEC Voltage")
        self.tec_voltage_value = QDoubleSpinBox()
        self.tec_voltage_value.setKeyboardTracking(False)
        self.tec_voltage_value.setDecimals(0)
        self.tec_voltage_value.setRange(0,28)
        self.tec_voltage_value.setSingleStep(1)
        self.tec_voltage_value.setValue(0)
        hsplitter4.addWidget(tecvoltagetitle)
        hsplitter4.addWidget(self.tec_voltage_value)

        layout = QVBoxLayout()
        layout.addWidget(self.sensor_status)
        layout.addWidget(hsplitter1)
        layout.addWidget(hsplitter2)
        layout.addWidget(hsplitter3)
        layout.addWidget(hsplitter4)

        self.sensorSettingsLayout.setLayout(layout)
        self.controllerSettingsLayout = QGroupBox("Controller Settings")

        hsplitter1 = QSplitter(Qt.Orientation.Horizontal, self)
        statustitle = QLabel("Status Period")
        self.status_period = QDoubleSpinBox()
        self.status_period.setKeyboardTracking(False)
        self.status_period.setDecimals(0)
        self.status_period.setRange(0,10000)
        self.status_period.setSingleStep(1)
        self.status_period.setValue(0)
        statusunit = QLabel("ms")
        hsplitter1.addWidget(statustitle)
        hsplitter1.addWidget(self.status_period)
        hsplitter1.addWidget(statusunit)

        hsplitter2 = QSplitter(Qt.Orientation.Horizontal, self)
        tracetitle = QLabel("Trace Level")
        self.trace_level = QDoubleSpinBox()
        self.trace_level.setKeyboardTracking(False)
        self.trace_level.setDecimals(0)
        self.trace_level.setRange(0,3)
        self.trace_level.setSingleStep(1)
        self.trace_level.setValue(0)
        hsplitter2.addWidget(tracetitle)
        hsplitter2.addWidget(self.trace_level)

        checkboxes = QGridLayout()
        moduletitle = QLabel("Module Enable")
        self.daq_0 = QCheckBox("DAQ [0]")
        self.daq_0.setDisabled(True)
        self.daq_1 = QCheckBox("DAQ [1]")
        self.daq_1.setDisabled(True)
        self.daq_2 = QCheckBox("DAQ [2]")
        self.daq_2.setDisabled(True)
        self.daq_3 = QCheckBox("DAQ [3]")
        self.daq_3.setDisabled(True)
        self.las_4 = QCheckBox("LAS [4]")
        self.sif_5 = QCheckBox("SIF [5]")
        self.flc_6 = QCheckBox("FLC [6]")
        self.extra_7 = QCheckBox("[7]")
        checkboxes.addWidget(moduletitle, 0, 0)
        checkboxes.addWidget(self.daq_0, 0, 1)
        checkboxes.addWidget(self.daq_1, 1, 1)
        checkboxes.addWidget(self.daq_2, 2, 1)
        checkboxes.addWidget(self.daq_3, 3, 1)
        checkboxes.addWidget(self.las_4, 0, 2)
        checkboxes.addWidget(self.sif_5, 1, 2)
        checkboxes.addWidget(self.flc_6, 2, 2)
        checkboxes.addWidget(self.extra_7, 3, 2)    

        layout = QVBoxLayout()
        layout.addWidget(hsplitter1)
        layout.addWidget(hsplitter2)
        layout.addLayout(checkboxes)

        self.controllerSettingsLayout.setLayout(layout)