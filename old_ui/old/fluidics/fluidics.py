"""
This is the fluidics UI and it sets up the threads for the fluidics event handler and the fluidics
communication
"""

import pyqtgraph as pg
from itertools import repeat
from time import sleep
#NOTE:  This is done so that it can be used both by fluidics main.py and ssm-kernel main.py
try:
    from fluidicsprobe import ProbeDialogWindow
    from fluidicsfilesave import sharedFluidicsFileClass
    from ui.fluidics.fluidicsupdater import FluidicsUIUpdater
except:
    from .fluidicsprobe import ProbeDialogWindow
    from .fluidicsfilesave import sharedFluidicsFileClass
    from .fluidicsupdater import FluidicsUIUpdater

from PyQt6 import QtCore
from PyQt6.QtCore import QThread, Qt
from PyQt6.QtWidgets import (QWidget, QGridLayout, QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QSplitter, QLineEdit, QProgressBar, QLabel, QTextEdit, QMessageBox, QInputDialog)

"""!
@package Fluidics Control Panel
This module includes the setup of the Fluidics Control tab and related object variables.
"""

class FluidicsControlPanel(QWidget):
    """!
    Creates the Fluidics Control Panel
    """
    def __init__(self, processor):
        """!
            Inputs:
                config:             (dict) This is an object that holds the fluidics config
                fluidics_processor:     (fluidicsController) Object that holds the data processor for
                                    fluidics

            Assigns:
                sample_flow:        (list) This is a list of points that will be updated and used
                                    to graph the sample flow 
                sheath_flow:        (list) This is a list of points that will be updated and used
                                    to graph the sheath flow
                time:               (list) This is a list of points that will be updated and used
                                    to graph time 
                fluidics_processor:     (fluidicsController) Holds the fluidics_processor object
                config:             (dict) Holds the config object passed in
        """
        super().__init__()
        ##  These are the flow rates that are read in, should we initialize them to 0?
        self.sample_flow = list(repeat(0, 10))
        self.sheath_flow = list(repeat(0, 10))
  
        self.current_sample_flow = 0
        self.current_sheath_flow = 0
        self.current_probe_step = 0
        self.current_probe_height = self.probe_step_to_height()
        self.time = list(range(10))

        self.probe_dialog_window = ProbeDialogWindow(control_panel=self)
        self.probe_dialog_window.hide()
        self.probe_dialog_visible = False
        
        #Prepare Layout
        fluidicsMainLayout = QGridLayout(self)
        
        self.createTopLeftBox()
        self.createBottomLeftBox()
        self.createTopRightBox()
        self.createBottomRightBox()
        self.createMiddleLeftBox()

        self.topLeftGroupBox.setMaximumWidth(300)
        self.middleLeftGroupBox.setMaximumWidth(300)
        self.bottomLeftGroupBox.setMaximumWidth(300)
        
        fluidicsMainLayout.addWidget(self.topLeftGroupBox, 0, 1)            #-> control panel
        fluidicsMainLayout.addWidget(self.middleLeftGroupBox, 0, 2)         #-> flow inputs
        fluidicsMainLayout.addWidget(self.topRightGroupBox, 0, 3)           #-> window terminal
        fluidicsMainLayout.addWidget(self.bottomRightGroupBox, 1, 0, 1, 4)  #-> plot
        fluidicsMainLayout.addWidget(self.bottomLeftGroupBox, 0, 0)         #-> dummy lights

        fluidicsMainLayout.setRowStretch(1,2)
        
        #Fluidics communication
        self.fluidics_processor = processor

        #Fluidics UI Backend
        self.ui_backend = FluidicsUIUpdater(self)
        self.ui_backend_thread = QThread()
        self.ui_backend.moveToThread(self.ui_backend_thread)
        
        #NOTE:  all function calls and everything else should happen in a thread, the only thing 
        #       that should happen in the panel is setting up the view
        self.ui_backend.update_buttons()
        
        print("Fluidics UI setup")

    def finish(self):
        if self.ui_backend_thread:
            self.ui_backend_thread.quit()
        print("Fluidics UI backend quit")

    def probe_step_to_height(self):
        return self.current_probe_step/100


    def createTopLeftBox(self):
        """!
        Control pane, this sets up the different buttons available to the user

        Assigns:
            Connect_button
            start_button
            stop_button
            clean_button
            feedback_button
            debubble_button
            backflush_button
            probeup_button
            probedown_button

        Inputs:
        Outputs:
        """
        
        self.topLeftGroupBox = QGroupBox("System Controls")
        layout = QGridLayout()

        self.connect_button = QPushButton("Connect")
        self.connect_button.setFixedSize(75, 40)
        # self.connect_button.clicked.connect(self.toggle_connection)

        self.start_button = QPushButton("Start")
        self.start_button.setFixedSize(75,40)
        # self.start_button.clicked.connect(lambda : self.command_input("START"))

        self.stop_button = QPushButton("Stop")
        self.stop_button.setFixedSize(75,40)
        # self.stop_button.clicked.connect(lambda: self.command_input("A"))

        self.clean_button = QPushButton("Clean")
        self.clean_button.setFixedSize(75,40)
        # self.clean_button.clicked.connect(self.clean_process)

        self.feedback_button = QPushButton("Feedback")
        self.feedback_button.setFixedSize(75,40)
        # self.feedback_button.clicked.connect(lambda : self.command_input("P"))

        self.debubble_button = QPushButton("Debubble")
        self.debubble_button.setFixedSize(75,40)
        # self.debubble_button.clicked.connect(lambda : self.command_input("B"))

        self.backflush_button = QPushButton("Backflush")
        self.backflush_button.setFixedSize(75,40)
        # self.backflush_button.clicked.connect(lambda : self.command_input("BF"))

        self.probeup_button = QPushButton("Home Probe")
        self.probeup_button.setFixedSize(75,40)
        # self.probeup_button.clicked.connect(lambda : self.command_input("SITH"))

        self.probedown_button = QPushButton("Move Probe")
        self.probedown_button.setFixedSize(75,40)
        # self.probedown_button.clicked.connect(lambda: self.command_input("SITL"))
        
        self.probedialog_button = QPushButton("Probe Alignment")
        self.probedialog_button.setFixedSize(235,40)
        # self.probedialog_button.clicked.connect(self.toggle_probe_dialog_window)
        
        self.boost_button = QPushButton("BOOST")
        self.boost_button.setFixedSize(235,40)

        print("Here at the buttons creation")
        self.systemIDButton = QPushButton("RunSystem ID")
        self.systemIDButton.setFixedSize(235, 40)

        layout.addWidget(self.connect_button, 0, 0)
        layout.addWidget(self.start_button, 0, 1)
        layout.addWidget(self.stop_button, 0, 2)
        layout.addWidget(self.clean_button, 1, 0)
        layout.addWidget(self.feedback_button, 1, 1)
        layout.addWidget(self.debubble_button, 1, 2)
        layout.addWidget(self.backflush_button, 2, 0)
        layout.addWidget(self.probeup_button, 2, 1)
        layout.addWidget(self.probedown_button, 2, 2)
        layout.addWidget(self.systemIDButton, 3, 0, 1, 3)
        layout.addWidget(self.probedialog_button, 4, 0, 1, 3)
        layout.addWidget(self.boost_button, 5, 0, 1, 3)
        self.topLeftGroupBox.setLayout(layout)
        
        
    def createMiddleLeftBox(self):
        """!
        This method creates the flow rate control boxes for the user to enter the sheath and sample
        flow rates, and also outputs the current values of each in a line below
        
        Assigns:
            sheathflow_label
            sheathflow_enter
            sheathflow_actual
            sampleflow_label
            sampleflow_enter
            sampleflow_actual
        
        Inputs: None
        Outputs: None
        """
        self.middleLeftGroupBox = QGroupBox("Flow Rate controls")
        layout = QGridLayout()
        
        self.sheathflow_label = QLabel("Sheath Delta")
        
        self.sheathflow_enter = QLineEdit()
        self.sheathflow_enter.setFixedSize(100, 40)
        self.sheathflow_actual = QLineEdit()
        self.sheathflow_actual.setFixedSize(100, 40)
        self.sheathflow_actual.setEnabled(False)
        
        self.sheathflow_button = QPushButton("Change Rate")
        self.sheathflow_button.setFixedSize(75,40)
        # self.sheathflow_button.clicked.connect(lambda : self.command_input(f"F {self.sheathflow_enter.displayText()}"))
        
        self.sampleflow_label = QLabel("Sample Delta")
        
        self.sampleflow_enter = QLineEdit()
        self.sampleflow_enter.setFixedSize(100, 40)
        self.sampleflow_actual = QLineEdit()
        self.sampleflow_actual.setFixedSize(100, 40)
        self.sampleflow_actual.setEnabled(False)
        
        self.sampleflow_button = QPushButton("Change Rate")
        self.sampleflow_button.setFixedSize(75,40)
        # self.sampleflow_button.clicked.connect(lambda : self.command_input(f"SON {self.sampleflow_enter.displayText()}"))
        
        layout.addWidget(self.sheathflow_label, 0, 0)
        layout.addWidget(self.sheathflow_button, 1, 0)
        layout.addWidget(self.sheathflow_enter, 2, 0)
        layout.addWidget(self.sheathflow_actual, 3, 0)
        
        layout.addWidget(self.sampleflow_label, 0, 1)
        layout.addWidget(self.sampleflow_button, 1, 1)
        layout.addWidget(self.sampleflow_enter, 2, 1)
        layout.addWidget(self.sampleflow_actual, 3, 1)
        
        self.middleLeftGroupBox.setLayout(layout)  
    
    def createTopRightBox(self):
        """!
        Sets up the window terminal, this allows the user to enter more specific commands than what
        is available in the buttons

        Assigns:
            command_line
            send_command
            command_output

        Inputs:
        Outputs:
        """
        self.topRightGroupBox = QGroupBox("Terminal")
        
        layout = QGridLayout()

        self.command_line = QLineEdit()
        self.command_line.setFixedSize(200,50)

        self.send_command = QPushButton("Enter")
        self.send_command.setFixedSize(100,50)
        # self.send_command.clicked.connect(lambda : self.command_input(self.command_line.text()))

        self.command_output =  QTextEdit()  #change -> QTextEdit
        self.command_output.setReadOnly(True)

        self.record_command = QPushButton("Record Sample Velocity")
        self.record_command.setFixedSize(200,50)
        #Map button to function 
        self.record_command.clicked.connect(sharedFluidicsFileClass.StartStopRecording)

        Vsplitter = QSplitter(Qt.Orientation.Vertical)
        Vsplitter.addWidget(self.command_line)
        Vsplitter.addWidget(self.send_command)
        Vsplitter.addWidget(self.record_command)


        layout.addWidget(Vsplitter)
        layout.addWidget(self.command_output, 0, 1)
        self.topRightGroupBox.setLayout(layout)
        
    def createBottomRightBox(self):
        """!
        These are the plots, sets up the graphs for sheathflow and sample flow

        Assigns:
            sheathflow_graph

        Inputs:
        Outputs:
        """
        ###condense to one grid please
        self.bottomRightGroupBox = QGroupBox("Data Output")

        styles = {"color": "red", "font-size": "18px"}

        self.sheathflow_graph = pg.PlotWidget()
        self.sheathflow_graph.setBackground("w")
        self.sheathflow_graph.showGrid(True, True)
        self.sheathflow_graph.setLabel('bottom', "Time", **styles)
        self.sheathflow_graph.setLabel('left', "Flow (rate/min)", **styles)
        self.sheathflow_graph.setTitle("Flow Rates", color="b", size="15pt")
        self.sheathflow_graph.setYRange(-0.2, 125)
        self.sheathflow_graph.setContentsMargins(0,0,50,0)
        legend = self.sheathflow_graph.addLegend()
        self.sheath_line = self.sheathflow_graph.plot(self.time, self.sheath_flow, 
                            pen=pg.mkPen(color=(0,0,0)))
        self.sample_line = self.sheathflow_graph.plot(self.time, self.sample_flow, 
                            pen=pg.mkPen(color=(0,0,255)))

        legend.addItem(self.sheath_line, 'Sheath (mL/min)')
        legend.addItem(self.sample_line, 'Sample (uL/min)')

        layout = QHBoxLayout()
        layout.addWidget(self.sheathflow_graph)
        self.bottomRightGroupBox.setLayout(layout)
        
        
    def createBottomLeftBox(self):
        """!
        These are the system status dummy lights, this is achieved by setting a progress bar to
        full and setting the chunk to red, this will need to be updated when each item is 
        connected and then changed to green.

        Assigns:
            sampleline_status
            pump_status
            pidcontrol_status
            tubedetect_status
            sheathlevel_status
            wastelevel_status
            probe_height

        Inputs:
        Outputs:
        """
        self.bottomLeftGroupBox = QGroupBox("System Status")
        layout = QVBoxLayout()

        hsplitter1 = QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        sheathflowtitle = QLabel("Sheath Flow (ml/min)")
        self.sheathflowval = QLabel(self) # this needs to have the number converted to str
        hsplitter1.addWidget(sheathflowtitle)
        hsplitter1.addWidget(self.sheathflowval)
        self.sheathflowval.setText(str(0))

        hsplitter2 = QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        sampleflowtitle = QLabel("Sample Flow (ml/min)")
        self.sampleflowval = QLabel(self) # this needs to have the number converted to str
        hsplitter2.addWidget(sampleflowtitle)
        hsplitter2.addWidget(self.sampleflowval)
        self.sampleflowval.setText(str(0))

        hsplitter3 = QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        vacuumtitle = QLabel("Vaccum Pressure (PSI)")
        self.vacuumval = QLabel(self) # this needs to have the number converted to str
        hsplitter3.addWidget(vacuumtitle)
        hsplitter3.addWidget(self.vacuumval)
        self.vacuumval.setText(str(0))

        hsplitter4 = QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        sampleVelocityTitle = QLabel("Sample Velocity (mm/s)")
        self.sampleVelocity = QLabel(self) # this needs to have the number converted to str
        hsplitter4.addWidget(sampleVelocityTitle)
        hsplitter4.addWidget(self.sampleVelocity)
        self.sampleVelocity.setText(str(0))

        self.sampleline_status = QProgressBar()
        self.sampleline_status.setFormat("Sample Line")
        self.sampleline_status.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.sampleline_status.setValue(100)
        self.sampleline_status.setStyleSheet("QProgressBar::chunk {background-color: red;}")

        self.pump_status = QProgressBar()
        self.pump_status.setFormat("Pump")
        self.pump_status.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.pump_status.setValue(100)
        self.pump_status.setStyleSheet("QProgressBar::chunk {background-color: red;}")
        
        self.pidcontrol_status = QProgressBar()
        self.pidcontrol_status.setFormat("PID Control")
        self.pidcontrol_status.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.pidcontrol_status.setValue(100)
        self.pidcontrol_status.setStyleSheet("QProgressBar::chunk {background-color: red;}")
        self.pidcontrol_status.state = 0

        self.tubedetect_status = QProgressBar()
        self.tubedetect_status.setFormat("Tube Detect")
        self.tubedetect_status.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.tubedetect_status.setValue(100)
        self.tubedetect_status.setStyleSheet("QProgressBar::chunk {background-color: red;}")

        self.sheathlevel_status = QProgressBar()
        self.sheathlevel_status.setFormat("Sheath Level")
        self.sheathlevel_status.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.sheathlevel_status.setValue(100)
        self.sheathlevel_status.setStyleSheet("QProgressBar::chunk {background-color: red;}")
        
        self.wastelevel_status = QProgressBar()   
        self.wastelevel_status.setFormat("Waste Level")
        self.wastelevel_status.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.wastelevel_status.setValue(100)
        self.wastelevel_status.setStyleSheet("QProgressBar::chunk {background-color: red;}")
        
        
        self.boost_status = QProgressBar()
        self.boost_status.setFormat("BOOST")
        self.boost_status.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.boost_status.setValue(100)
        self.boost_status.setStyleSheet("QProgressBar::chunk {background-color: red;}")
        self.boost_status.state = 0

        self.recording_status = QProgressBar()
        self.recording_status.setFormat("Recording")
        self.recording_status.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.recording_status.setValue(100)
        self.recording_status.setStyleSheet("QProgressBar::chunk {background-color: red;}")
        self.recording_status.state = 0

        layout.addWidget(hsplitter1)
        layout.addWidget(hsplitter2)
        layout.addWidget(hsplitter3)
        layout.addWidget(hsplitter4)
        layout.addWidget(self.sampleline_status)
        layout.addWidget(self.pump_status)
        layout.addWidget(self.pidcontrol_status)
        layout.addWidget(self.tubedetect_status)
        layout.addWidget(self.sheathlevel_status)
        layout.addWidget(self.wastelevel_status)
        layout.addWidget(self.boost_status)
        layout.addWidget(self.recording_status)
        self.bottomLeftGroupBox.setLayout(layout)


    """
    Pulled from flow_plotter.py
    Updated value:              Corresponding tuple location
    sheath_data                 status[0]
    sample_data                 status[1]
    sample_line_state           status[2]
    pid_control_state           status[3]
    tube_update_state           status[4]
    sheath_level                status[5]
    waste_level                 status[6]
    manual_move                 status[]   ########### REMOVED ##############
    pump_state                  status[7]
    current_step                status[8]
    """

    def clean_process(self):
        """!
        This method is called when the clean button is pressed and it sends a series of commands to
        clean the fluidics system

        Assigns:

        Inputs:
        Outputs:
        """
        sleepTime = 5
        message = QMessageBox()

        #NOTE:  There needs to be a way to break out but also needs to not allow commands through when
        #       cleaning is being run

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.feedback_button.setEnabled(False)
        self.debubble_button.setEnabled(False)
        self.backflush_button.setEnabled(False)
        self.probeup_button.setEnabled(False)
        self.probedown_button.setEnabled(False)
        self.sheathflow_button.setEnabled(False)
        self.sampleflow_button.setEnabled(False)
        self.probedialog_button.setEnabled(False)
        self.connect_button.setEnabled(False)
        self.clean_button.setEnabled(False)
        self.systemIDButton.setEnabled(False)

        self.fluidics_processor.clean_flag = True

        nextButton = message.addButton(QMessageBox.StandardButton.Ok)
        nextButton.setText("Next")
        quitButton = message.addButton(QMessageBox.StandardButton.Cancel)
        quitButton.setText("Quit")        
        
        message.setText("Step 1: Bleach wash\n\nPut in 3ml 10% bleach...\nPress Next when ready to start")
        button = message.exec()
        print(button)

        if button != QMessageBox.StandardButton.Ok:
            self.ui_backend.update_buttons()
            self.fluidics_processor.clean_flag = False
            return
        ##Commands
        self.fluidics_processor.send_command("STIL")
        self.fluidics_processor.send_command("RESTART") 
        self.fluidics_processor.send_command("SON 120")
        self.fluidics_processor.send_command("CON") 
        self.fluidics_processor.send_command("F 1") 
        self.fluidics_processor.send_command("P 1")
        sleep(sleepTime)
        self.fluidics_processor.send_command("SOFF")
        self.fluidics_processor.send_command("P 0")
        self.fluidics_processor.send_command("SITH") 
        # print("This is where we send commands")
        self.command_output.append("Commands sent\n\n")

        message.setText("Step 2: Water rinse\n\nPut in 3ml deionized water...\nPress Next when ready to start")
        button = message.exec()

        if button != QMessageBox.StandardButton.Ok:
            self.ui_backend.update_buttons()
            self.fluidics_processor.clean_flag = False
            return
        ##Commands
        self.fluidics_processor.send_command("STIL")
        self.fluidics_processor.send_command("RESTART") 
        self.fluidics_processor.send_command("SON 120")
        self.fluidics_processor.send_command("CON") 
        self.fluidics_processor.send_command("F 1") 
        self.fluidics_processor.send_command("P 1")
        sleep(sleepTime)
        self.fluidics_processor.send_command("SOFF")
        self.fluidics_processor.send_command("P 0")
        self.fluidics_processor.send_command("SITH")
        self.command_output.append("Commands sent\n\n")

        message.setText("Step 3: Contrad Cleaning\n\nPress Next when ready to start")
        button = message.exec()

        if button != QMessageBox.StandardButton.Ok:
            self.ui_backend.update_buttons()
            self.fluidics_processor.clean_flag = False
            return
        ##Commands
        self.fluidics_processor.send_command("STIL")
        self.fluidics_processor.send_command("RESTART") 
        self.fluidics_processor.send_command("SON 120")
        self.fluidics_processor.send_command("CON") 
        self.fluidics_processor.send_command("F 1") 
        self.fluidics_processor.send_command("P 1")
        sleep(sleepTime)
        self.fluidics_processor.send_command("SOFF")
        self.fluidics_processor.send_command("P 0")
        self.fluidics_processor.send_command("SITH")
        self.command_output.append("Commands sent\n\n")

        message.setText("Step 4: Final rinse\n\nPress Next when ready to start")
        button = message.exec()

        if button != QMessageBox.StandardButton.Ok:
            self.ui_backend.update_buttons()
            self.fluidics_processor.clean_flag = False
            return
        ##Commands
        self.fluidics_processor.send_command("STIL")
        self.fluidics_processor.send_command("RESTART") 
        self.fluidics_processor.send_command("SON 120")
        self.fluidics_processor.send_command("CON") 
        self.fluidics_processor.send_command("F 1") 
        self.fluidics_processor.send_command("P 1")
        sleep(sleepTime)
        self.fluidics_processor.send_command("COFF")
        self.fluidics_processor.send_command("A")
        self.command_output.append("Last Commands sent\n\n")

        sleep(1)

        self.fluidics_processor.close_connection()
        self.connect_button.setText("Connect")


    def CreatePopUpBoxToAttainListValues(self, windowTitleText, mainText, options, current, editable):
        try:
            value, ok = QInputDialog.getItem(self, windowTitleText, mainText, options, current, editable)
        except Exception as e:
            print("There was an issue with getting the value from the pop-up box... Aborting...")
            print(f"Here was the Exception: {e}")
            return(None)
        if ok:
            return(value) #If the user pressed the OK button
        else:
            return(None) #If the user pressed the cancel button

    def CreatePopUpBoxToAttainInputValues(self, windowTitleText, mainText, xSize, ySize):
        titlePopUp = QInputDialog(self)
        titlePopUp.setWindowTitle(windowTitleText)
        titlePopUp.setLabelText(mainText)
        titlePopUp.resize(xSize, ySize)

        if titlePopUp.exec(): #If text has been input
            value = titlePopUp.textValue()
            if not value: #If not tile was entered
                return(None)
            else:
                return(value)
            
    def ConvertStrToInt(self, value):
        try:
            value = int(value)
            return(value)
        except Exception as e:
            print(f"Exception when converting from sting to integer number: {e}")
            return None


