import os
import sys

import numpy as np
import time

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from proto import schema_pb2, shared_pb2, command_pb2
from google.protobuf import text_format


#TODO:  File all items that need to be called from the control panel
class MainboardUpdater(QObject):
    def __init__(self, mainboard, controlpanel):
        super().__init__()
        
        self.mainboard = mainboard
        self.controlpanel = controlpanel
        
        self.controlpanel.com_port_connect.pressed.connect(self.connect_mainboard)
        
        # self.controlpanel.daqcapturemodeselect.currentIndexChanged.connect(self.apply_settings)
        # self.controlpanel.daqcapturelengthselect.currentIndexChanged.connect(self.apply_settings)
        # self.controlpanel.daqcaptureoffsetselect.currentIndexChanged.connect(self.apply_settings)

        # self.controlpanel.atcdselect.currentIndexChanged.connect(self.apply_settings)
        # self.controlpanel.atccselect.textChanged.connect(self.apply_settings)
        # self.controlpanel.atpselect.currentIndexChanged.connect(self.apply_settings)
        # self.controlpanel.athreshselect.valueChanged.connect(self.apply_settings)
        # self.controlpanel.ahystselect.valueChanged.connect(self.apply_settings)

        # self.controlpanel.daq0Math.stateChanged.connect(self.apply_settings)
        # self.controlpanel.daq1Math.stateChanged.connect(self.apply_settings)
        # self.controlpanel.daq2Math.stateChanged.connect(self.apply_settings)
        # self.controlpanel.daq3Math.stateChanged.connect(self.apply_settings)
        # self.controlpanel.baseline_polarity.currentIndexChanged.connect(self.apply_settings)
        # self.controlpanel.baseline_smoothing.currentIndexChanged.connect(self.apply_settings)
        # self.controlpanel.baseline_slew_rate.currentIndexChanged.connect(self.apply_settings)

        self.controlpanel.nop.clicked.connect(self.send_nop)
        self.controlpanel.daq_ver_info.clicked.connect(self.request_version)
        self.controlpanel.daq_settings.clicked.connect(self.request_settings)
        self.controlpanel.daq_apply.clicked.connect(self.apply_settings)

        # self.controlpanel.pulse_setting.valueChanged.connect(self.apply_settings)
        # self.controlpanel.delay_setting.valueChanged.connect(self.apply_settings)
        # self.controlpanel.on_time_setting.valueChanged.connect(self.apply_settings)
        # self.controlpanel.off_time_setting.valueChanged.connect(self.apply_settings)

        # self.controlpanel.laser_mode[0].currentIndexChanged.connect(self.apply_settings)
        # self.controlpanel.laser_seq[0].valueChanged.connect(self.apply_settings)
        # self.controlpanel.laser_power[0].valueChanged.connect(self.apply_settings)
        # self.controlpanel.laser_tec[0].clicked.connect(self.apply_settings)

        # self.controlpanel.laser_mode[1].currentIndexChanged.connect(self.apply_settings)
        # self.controlpanel.laser_seq[1].valueChanged.connect(self.apply_settings)
        # self.controlpanel.laser_power[1].valueChanged.connect(self.apply_settings)
        # self.controlpanel.laser_tec[1].clicked.connect(self.apply_settings)

        # self.controlpanel.laser_mode[2].currentIndexChanged.connect(self.apply_settings)
        # self.controlpanel.laser_seq[2].valueChanged.connect(self.apply_settings)
        # self.controlpanel.laser_power[2].valueChanged.connect(self.apply_settings)
        # self.controlpanel.laser_tec[2].clicked.connect(self.apply_settings)

        # self.controlpanel.laser_mode[3].currentIndexChanged.connect(self.apply_settings)
        # self.controlpanel.laser_seq[3].valueChanged.connect(self.apply_settings)
        # self.controlpanel.laser_power[3].valueChanged.connect(self.apply_settings)
        # self.controlpanel.laser_tec[3].clicked.connect(self.apply_settings)

        # self.controlpanel.laser_mode[4].currentIndexChanged.connect(self.apply_settings)
        # self.controlpanel.laser_seq[4].valueChanged.connect(self.apply_settings)
        # self.controlpanel.laser_power[4].valueChanged.connect(self.apply_settings)
        # self.controlpanel.laser_tec[4].clicked.connect(self.apply_settings)

        # self.controlpanel.laser_mode[5].currentIndexChanged.connect(self.apply_settings)
        # self.controlpanel.laser_seq[5].valueChanged.connect(self.apply_settings)
        # self.controlpanel.laser_power[5].valueChanged.connect(self.apply_settings)
        # self.controlpanel.laser_tec[5].clicked.connect(self.apply_settings)

        # self.controlpanel.status_period.valueChanged.connect(self.apply_settings)
        # self.controlpanel.trace_level.valueChanged.connect(self.apply_settings)
        # self.controlpanel.daq_0.clicked.connect(self.apply_settings)
        # self.controlpanel.daq_1.clicked.connect(self.apply_settings)
        # self.controlpanel.daq_2.clicked.connect(self.apply_settings)
        # self.controlpanel.daq_3.clicked.connect(self.apply_settings)
        # self.controlpanel.las_4.clicked.connect(self.apply_settings)
        # self.controlpanel.sif_5.clicked.connect(self.apply_settings)
        # self.controlpanel.flc_6.clicked.connect(self.apply_settings)
        # self.controlpanel.extra_7.clicked.connect(self.apply_settings)

        # self.controlpanel.voltage_value.valueChanged.connect(self.apply_settings)
        # self.controlpanel.tec_settings.currentIndexChanged.connect(self.apply_settings)
        # self.controlpanel.temp_value.valueChanged.connect(self.apply_settings)
        # self.controlpanel.tec_voltage_value.valueChanged.connect(self.apply_settings)
        self.mainboard.received.connect(self.received_message)

    def connect_mainboard(self):
        #TODO:  Do we want just a mainboard connection status?
        if self.mainboard.change_connection(self.controlpanel.com_port_edit.text()) == "connect":
            print(f"We got back connect: {self.controlpanel.com_port_edit.text()}")
            #TODO:  Update everything for the mainboard to respect the state of mainboard (MB) or daq (DAQ)
            # self.controlpanel.daq_connection = "DAQ"
            self.controlpanel.daq_connection = "MB"
            self.request_settings()
            self.controlpanel.com_port_connect.setText("Disconnect")
        else:
            print("Disconnected from mainboard")
            self.controlpanel.daq_connection = "Player"
            self.controlpanel.com_port_connect.setText("Connect")
            self.controlpanel.com_port_edit.setText("")
        self.controlpanel.ui_backend.set_button_states()

    def send_nop(self):
        # if self.controlpanel.daq_connection != "DAQ":
        if self.controlpanel.daq_connection not in ["DAQ", "MB"]:
            return
        hm = schema_pb2.HostMessage()
        hm.command.nop.SetInParent()
        self.send_message(hm)

    def request_settings(self):
        # if self.controlpanel.daq_connection != "DAQ":
        if self.controlpanel.daq_connection not in ["DAQ", "MB"]:
            return
        hm = schema_pb2.HostMessage()
        hm.command.request.request_type = command_pb2.CommandRequest.RequestType.Settings
        self.send_message(hm)

    def apply_settings(self):
        # if self.controlpanel.daq_connection != "DAQ":
        if self.controlpanel.daq_connection not in ["DAQ", "MB"]:
            return
        hm = schema_pb2.HostMessage()
        settings = shared_pb2.Settings()

        # Controller Settings
        settings.module_enable.extend([checkbox.isChecked() for checkbox in [self.controlpanel.daq_0, self.controlpanel.daq_1, 
                                        self.controlpanel.daq_2, self.controlpanel.daq_3, self.controlpanel.las_4, 
                                        self.controlpanel.sif_5, self.controlpanel.flc_6, self.controlpanel.extra_7]])
        settings.trace_level = int(self.controlpanel.trace_level.value())
        settings.report_period = int(self.controlpanel.status_period.value())
        # settings.report_period = self.view.report_period_spinbox.value()

        # Capture Settings
        settings.capture_trigger = self.controlpanel.daqcapturemodeselect.currentIndex()
        settings.capture_length = self.controlpanel.daqcapturelengthselect.currentIndex()
        settings.capture_delay = self.controlpanel.daqcaptureoffsetselect.currentIndex()

        # Analog Trigger Settings
        settings.atrig_daq_module = self.controlpanel.atcdselect.currentIndex()
        settings.atrig_daq_channel = int(self.controlpanel.atccselect.value())
        settings.atrig_polarity = False if self.controlpanel.atpselect.currentIndex() == 0 else True
        settings.atrig_threshold = int(((self.controlpanel.athreshselect.value() / 0.6) * 32768) + 32768)
        self.controlpanel.thresh_line.setPos(self.controlpanel.athreshselect.value())
        settings.atrig_hysteresis = int((self.controlpanel.ahystselect.value() / 0.6) * 32768)

        # Baseline Subtraction Function
        mathEnabled = [cb.isChecked() for cb in [self.controlpanel.daq0Math, self.controlpanel.daq1Math, self.controlpanel.daq2Math, self.controlpanel.daq3Math]]
        settings.math_enable.extend(mathEnabled)
        settings.baseline_polarity = self.controlpanel.baseline_polarity.currentIndex()
        settings.baseline_smoothing = self.controlpanel.baseline_smoothing.currentIndex()
        settings.baseline_slew_rate = self.controlpanel.baseline_slew_rate.currentIndex()

        # Laser Settings
        for n in range(6):
            laser = shared_pb2.LaserSettings()
            laser.mode = self.controlpanel.laser_mode[n].currentIndex()
            laser.power = int(self.controlpanel.laser_power[n].value() * 100)
            laser.timed_index = int(self.controlpanel.laser_seq[n].value())
            laser.tec_enabled = self.controlpanel.laser_tec[n].isChecked()
            settings.laser_settings.extend([laser])
        
        # Timer Settings
        settings.pulse_timer_n_pulses = int(self.controlpanel.pulse_setting.value())
        settings.pulse_timer_delay = int(self.controlpanel.delay_setting.value())
        settings.pulse_timer_t_on = int(self.controlpanel.on_time_setting.value())
        settings.pulse_timer_t_off = int(self.controlpanel.off_time_setting.value())

        # Sensor Settings
        settings.sensor_voltage = (self.controlpanel.voltage_value.value())
        settings.sensor_tec_mode = int(self.controlpanel.tec_settings.currentIndex())
        settings.sensor_tec_temperature = (self.controlpanel.temp_value.value())
        settings.sensor_tec_voltage = (self.controlpanel.tec_voltage_value.value())

        hm.command.apply.settings.CopyFrom(settings)
        self.send_message(hm)

        # self.trigger_channel = int((self.controlpanel.atcdselect.currentIndex() * 12) + int(self.controlpanel.atccselect.value()))
        # self.controlpanel.terminal_out.append(f"< new trigger channel: {self.trigger_channel}")
        # self.controlpanel.terminal_out.verticalScrollBar().setValue(self.terminal_out.verticalScrollBar().maximum())

    def settings_received(self, settings):
        #Controller Settings
        mods = [self.controlpanel.daq_0, self.controlpanel.daq_1, self.controlpanel.daq_2, self.controlpanel.daq_3, self.controlpanel.las_4, self.controlpanel.sif_5, self.controlpanel.flc_6, self.controlpanel.extra_7]

        for i, enable in enumerate(settings.module_enable):
            mods[i].setChecked(enable)
        self.controlpanel.trace_level.setValue(settings.trace_level)
        self.controlpanel.status_period.setValue(settings.report_period)

        # Capture Settings
        self.controlpanel.daqcapturemodeselect.setCurrentIndex(settings.capture_trigger)
        self.controlpanel.daqcapturelengthselect.setCurrentIndex(settings.capture_length)
        self.controlpanel.daqcaptureoffsetselect.setCurrentIndex(settings.capture_delay)

        # Analog Trigger Settings
        self.controlpanel.atcdselect.setCurrentIndex(settings.atrig_daq_module)
        self.controlpanel.atccselect.setValue(settings.atrig_daq_channel)
        self.controlpanel.trigger_channel = int((self.controlpanel.atcdselect.currentIndex() * 12) + self.controlpanel.atccselect.value())
        self.controlpanel.atpselect.setCurrentIndex(1 if settings.atrig_polarity else 0)
        self.controlpanel.athreshselect.setValue(((settings.atrig_threshold - 32768) / 32768.0)*0.6)
        self.controlpanel.thresh_line.setPos(self.controlpanel.athreshselect.value())
        self.controlpanel.ahystselect.setValue((settings.atrig_hysteresis / 32768) * 0.6)

        ###################################################################
        # self.controlpanel.atcdselect.setCurrentIndex(settings.atrig_daq_module)
        # self.controlpanel.atccselect.setValue(settings.atrig_daq_channel)
        # self.controlpanel.trigger_channel = int((self.controlpanel.atcdselect.currentIndex() * 12) + self.controlpanel.atccselect.value())
        # self.controlpanel.terminal_out.append(f"< new trigger channel: {self.controlpanel.trigger_channel}")
        # self.controlpanel.terminal_out.verticalScrollBar().setValue(self.controlpanel.terminal_out.verticalScrollBar().maximum())
        # self.controlpanel.atpselect.setCurrentIndex(1 if settings.atrig_polarity else 0)
        # self.controlpanel.athreshselect.setValue(((settings.atrig_threshold - 32768) / 32768.0)*0.6)
        # self.controlpanel.thresh_line.setPos(self.controlpanel.athreshselect.value())
        # self.controlpanel.ahystselect.setValue((settings.atrig_hysteresis / 32768) * 0.6)
        # self.controlpanel.hyst_line_top.setPos(self.controlpanel.athreshselect.value() + self.controlpanel.ahystselect.value())
        # self.controlpanel.hyst_line_bot.setPos(self.controlpanel.athreshselect.value() - self.controlpanel.ahystselect.value())
        ###################################################################

        # Baseline Subtraction Function
        mathEnabled = settings.math_enable
        self.controlpanel.daq0Math.setChecked(mathEnabled[0])
        self.controlpanel.daq1Math.setChecked(mathEnabled[1])
        self.controlpanel.daq2Math.setChecked(mathEnabled[2])
        self.controlpanel.daq3Math.setChecked(mathEnabled[3])
        self.controlpanel.baseline_polarity.setCurrentIndex(settings.baseline_polarity)
        self.controlpanel.baseline_smoothing.setCurrentIndex(settings.baseline_polarity)
        self.controlpanel.baseline_slew_rate.setCurrentIndex(settings.baseline_polarity)

        # Laser Settings
        for n in range(6):
            laser = settings.laser_settings[n]
            self.controlpanel.laser_mode[n].setCurrentIndex(laser.mode)
            self.controlpanel.laser_power[n].setValue(laser.power/100)
            self.controlpanel.laser_seq[n].setValue(laser.timed_index)
            self.controlpanel.laser_tec[n].setChecked(laser.tec_enabled)
        
        # Timer Settings
        self.controlpanel.pulse_setting.setValue(settings.pulse_timer_n_pulses)
        self.controlpanel.delay_setting.setValue(settings.pulse_timer_delay)
        self.controlpanel.on_time_setting.setValue(settings.pulse_timer_t_on)
        self.controlpanel.off_time_setting.setValue(settings.pulse_timer_t_off)

        # Sensor Settings
        self.controlpanel.voltage_value.setValue(settings.sensor_voltage)
        self.controlpanel.tec_settings.setCurrentIndex(int(settings.sensor_tec_mode))
        self.controlpanel.temp_value.setValue(settings.sensor_tec_temperature)
        self.controlpanel.tec_voltage_value.setValue(settings.sensor_tec_voltage)
        
    def status_received(self, status):
        # Laser Status
        if status.laser.connected:
            self.controlpanel.laser_status.setStyleSheet("QProgressBar::chunk {background-color: green;}")
        else:
            self.controlpanel.laser_status.setStyleSheet("QProgressBar::chunk {background-color: red;}")
        
        # Sensor Settings
        if status.sensor.connected:
            self.controlpanel.sensor_status.setStyleSheet("QProgressBar::chunk {background-color: green;}")
        else:
            self.controlpanel.sensor_status.setStyleSheet("QProgressBar::chunk {background-color: red;}")

    def request_version(self):
        # if self.controlpanel.daq_connection != "DAQ":
        if self.controlpanel.daq_connection not in ["DAQ", "MB"]:
            return
        hm = schema_pb2.HostMessage()
        hm.command.request.request_type = command_pb2.CommandRequest.RequestType.Version
        self.send_message(hm)

    def version_received(self, version):
        #TODO:  Consider changing exec to show since exec locks the thread
        dlg = QMessageBox()
        dlg.setWindowTitle("Version Info")
        dlg.setText(text_format.MessageToString(version))
        dlg.exec()
        
    def send_message(self, hm):
        self.mainboard.send(hm)
        self.controlpanel.terminal_out.append(f"> {text_format.MessageToString(hm)}")
        self.controlpanel.terminal_out.verticalScrollBar().setValue(self.controlpanel.terminal_out.verticalScrollBar().maximum())

    def received_message(self, cm):
        #TODO:  Add the other report styles and comment them out for potential later use
        if cm.HasField("report"):
            if cm.report.HasField("settings"):
                self.settings_received(cm.report.settings)
            elif cm.report.HasField("version"):
                self.version_received(cm.report.version)
            
            if cm.report.HasField("status"):
                self.status_received(cm.report.status)

            self.controlpanel.terminal_out.append(f"< {text_format.MessageToString(cm)}")
            self.controlpanel.terminal_out.verticalScrollBar().setValue(self.controlpanel.terminal_out.verticalScrollBar().maximum())