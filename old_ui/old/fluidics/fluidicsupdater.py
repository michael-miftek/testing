from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QPoint
#For fluidics file save
try:
    from fluidicsfilesave import sharedFluidicsFileClass
except:
    from .fluidicsfilesave import sharedFluidicsFileClass
import time
from time import sleep


class FluidicsUIUpdater(QObject):
    def __init__(self, controlpanel):
        super().__init__()

        self.processor = controlpanel.fluidics_processor
        self.control_panel = controlpanel
        self.time = [0,0,0,0,0,0,0,0,0,0]
        self.sample_flow = [0,0,0,0,0,0,0,0,0,0]
        self.sheath_flow = [0,0,0,0,0,0,0,0,0,0]

        #TODO: remove
        self.processor.error.connect(self.error_output)
        self.processor.command_return.connect(self.error_output)
        self.processor.ui_update.connect(self.update_plot_buttons)
        self.processor.opened.connect(self.update_buttons)

        self.control_panel.connect_button.clicked.connect(self.toggle_connection)
        self.control_panel.start_button.clicked.connect(lambda : self.command_input("START"))
        self.control_panel.stop_button.clicked.connect(lambda: self.command_input("A"))
        #TODO:  Should speak with fluidics team about how to set this up, and then with that will
        #       come information on if this should exist as part of the ui or if it should only be
        #       in the communication layer.
        self.control_panel.clean_button.clicked.connect(self.control_panel.clean_process)
        self.control_panel.feedback_button.clicked.connect(lambda : self.command_input("P"))
        self.control_panel.debubble_button.clicked.connect(lambda : self.command_input("B"))
        self.control_panel.backflush_button.clicked.connect(lambda : self.command_input("BF"))
        self.control_panel.probeup_button.clicked.connect(lambda : self.command_input("SITH"))
        #NOTE:  Change for live, Zilin has asked about added a menu drop down to select the number
        #       instead of the lambda call a menu and then setup the menu with the option and then call
        #       command_input with the STIL and number
        # self.control_panel.probedown_button.clicked.connect(lambda: self.command_input("SITL"))
        self.control_panel.probedown_button.clicked.connect(lambda:self.prob_menu())
        self.control_panel.boost_button.clicked.connect(lambda: self.command_input("BOOST"))
        self.control_panel.probedialog_button.clicked.connect(self.toggle_probe_dialog_window)

        self.control_panel.sheathflow_button.clicked.connect(lambda : self.command_input(f"F {self.control_panel.sheathflow_enter.displayText()}"))
        self.control_panel.sampleflow_button.clicked.connect(lambda : self.send_commands_with_sitl(f"SON {self.control_panel.sampleflow_enter.displayText()}"))
        self.control_panel.send_command.clicked.connect(lambda : self.command_input(self.control_panel.command_line.text()))

        #For the system ID
        self.control_panel.systemIDButton.clicked.connect(self.StartSystemIDMap)

        print("Fluidics UI Backend setup")

    def error_output(self, message):
        self.control_panel.command_output.append(f"> {message}")

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
    pump_state                  status[7]
    vcuum_val                   status[8]
    boost                       status[9]
    sampleVelocity              status[10]
    sheathPumpState             status[11]
    wastePumpState              status[12]
    sampleTarget                status[13]
    proportionalValveSteps      status[14]
    sampleDerivative            status[15]
    bubbleDetected              status[16]
    """
    def update_plot_buttons(self, status):
        """!
        This method is called when a visual update is emitted from the controller, it changes all
        appropriate status bars and updates the plot as needed.
        """
        
        if status[2] == 1: 
            self.control_panel.sampleline_status.setStyleSheet("QProgressBar::chunk {background-color: green;}") 
        else:
            self.control_panel.sampleline_status.setStyleSheet("QProgressBar::chunk {background-color: red;}")    

        if status[3] == 1: 
            self.control_panel.pidcontrol_status.setStyleSheet("QProgressBar::chunk {background-color: green;}") 
            self.control_panel.pidcontrol_status.state = 1
        else:
            self.control_panel.pidcontrol_status.setStyleSheet("QProgressBar::chunk {background-color: red;}")
            self.control_panel.pidcontrol_status.state = 0

        if status[4] == 1: 
            self.control_panel.tubedetect_status.setStyleSheet("QProgressBar::chunk {background-color: green;}") 
        else:
            self.control_panel.tubedetect_status.setStyleSheet("QProgressBar::chunk {background-color: red;}")

        if status[5] == 1: 
            self.control_panel.sheathlevel_status.setStyleSheet("QProgressBar::chunk {background-color: green;}") 
        else:
            self.control_panel.sheathlevel_status.setStyleSheet("QProgressBar::chunk {background-color: red;}")
            
        if status[6] == 0: 
            self.control_panel.wastelevel_status.setStyleSheet("QProgressBar::chunk {background-color: green;}") 
        else:
            self.control_panel.wastelevel_status.setStyleSheet("QProgressBar::chunk {background-color: red;}")
        
        if status[7] == 1: 
            self.control_panel.pump_status.setStyleSheet("QProgressBar::chunk {background-color: green;}") 
        else:
            self.control_panel.pump_status.setStyleSheet("QProgressBar::chunk {background-color: red;}")
            
        if status[9] == 1:
            self.control_panel.boost_status.setStyleSheet("QProgressBar::chunk {background-color: green;}") 
            self.control_panel.boost_status.state = 1
        else:
            self.control_panel.boost_status.setStyleSheet("QProgressBar::chunk {background-color: red;}")
            self.control_panel.boost_status.state = 0

        if  sharedFluidicsFileClass.buttonState == 1:
            self.control_panel.recording_status.setStyleSheet("QProgressBar::chunk {background-color: green;}") 
        else:
            self.control_panel.recording_status.setStyleSheet("QProgressBar::chunk {background-color: red;}")

        #Call live_update_plot here
        self.live_update_plot(status[0], status[1], status[8], status[10], status[11], status[12], status[13], status[14], status[15], status[16])
        self.control_panel.sheathflow_actual.setText(str(status[0]) + " ml")
        self.control_panel.sampleflow_actual.setText(str(status[1]) + " ul")
        if self.processor.unlock_system == True:
            self.update_start()

    def live_update_plot(self, newsheath, newsample, newvacuum, newSampleVelocity, sheathPumpState, wastePumpState, sampleTarget, proportionalValveSteps, sampleDerivative, bubbleDetected):
        """!
        This method is called to update the plot for both sample and sheath flow rates, it is
        connected to the data processor for fluidics being updated

        Assigns:
            time
            sheath_flow
            sample_flow

        Inputs:
        Outputs:
        """

        self.sheath_flow.append(newsheath)
        self.sample_flow.append(newsample)

        self.time.append(self.time[-1] + 1)
        
        self.time = self.time[1:]
        self.sheath_flow = self.sheath_flow[1:]
        self.sample_flow = self.sample_flow[1:]

        self.control_panel.sheath_line.setData(self.time,  self.sheath_flow)
        self.control_panel.sample_line.setData(self.time,  self.sample_flow)

        self.control_panel.sheathflowval.setText(str(newsheath))
        self.control_panel.sampleflowval.setText(str(newsample))

        self.control_panel.vacuumval.setText(str(newvacuum))

        self.control_panel.sampleVelocity.setText(str(newSampleVelocity))
        #If the user has chosen to record
        if(sharedFluidicsFileClass.buttonState):
            sharedFluidicsFileClass.append_data_to_file(sharedFluidicsFileClass.fileName, sharedFluidicsFileClass.get_timestamp() + "\t\t" + str(newSampleVelocity) + "\t\t\t" +  str(newsheath) + "\t\t\t" +  str(newsample) + "\t\t" + str(newvacuum) + "\t\t" + str(int(sheathPumpState)) + "\t\t" + str(int(wastePumpState)) + "\t\t" + str(sampleTarget) + "\t\t" + str(int(proportionalValveSteps)) + "\t\t" + str(sampleDerivative) + "\t\t" + str(int(bubbleDetected)) + '\n')    

        # self.current_sheath_flow = newsheath
        # self.current_sample_flow = newsample
        # self.vacuum_val = newvacuum

        # self.control_panel.sheathflowval.setText(str(self.current_sheath_flow))
        # self.control_panel.sampleflowval.setText(str(self.current_sample_flow))
        # self.control_panel.vaccumval.setText(str(self.vacuum_val))

    def toggle_connection(self):
        if not self.processor.connection:
            #TODO:  Add a pop up that asks for COM port and baud rate
            #TODO:  Fix fluidics service to be more like an API
            self.processor.open_connection('COM10', '115200')
            self.control_panel.connect_button.setText("Disconnect")
            self.update_buttons()
        
        else:
            self.processor.close_connection()
            self.control_panel.connect_button.setText("Connect")
            self.update_buttons()

    def toggle_probe_dialog_window(self):
        """!
        This is the probe alignment dialog window. Sets the probe ride height 
        and in the future, possibly the grid location of the needle 

        TODO: We need a way to ask the fluidics module what the current probe
        setting is. 

        Assigns:
            probe parameters

        Inputs:
        Outputs: 
        """
        if self.control_panel.probe_dialog_window.isHidden:
            self.processor.send_command("SITH")
            self.control_panel.probe_dialog_window.show()
        else:
            self.control_panel.probe_dialog_window.hide()

    def update_buttons(self):
        """!
        This method is called to update the buttons so that new commands can not be sent while the
        fluidics controller is running a current command or it is not connected
        
        Assigns:
        
        Inputs:
        Outputs:
        """
        if not self.processor.connection:

            self.control_panel.start_button.setEnabled(False)
            self.control_panel.stop_button.setEnabled(False)
            self.control_panel.feedback_button.setEnabled(False)

            self.control_panel.debubble_button.setEnabled(False)
            self.control_panel.backflush_button.setEnabled(False)
            self.control_panel.probeup_button.setEnabled(False)
            self.control_panel.probedown_button.setEnabled(False)
            self.control_panel.sheathflow_button.setEnabled(False)
            self.control_panel.sampleflow_button.setEnabled(False)
            self.control_panel.probedialog_button.setEnabled(False)
            self.control_panel.clean_button.setEnabled(False)
            self.control_panel.boost_button.setEnabled(False)
            self.control_panel.systemIDButton.setEnabled(False)
            #TODO: add in context switch here for the probe dialog

        else:

            # self.control_panel.start_button.setEnabled(True)
            self.control_panel.stop_button.setEnabled(True)
            # self.control_panel.feedback_button.setEnabled(True)
            self.control_panel.debubble_button.setEnabled(True)
            self.control_panel.backflush_button.setEnabled(True)
            self.control_panel.probeup_button.setEnabled(True)
            # self.control_panel.probedown_button.setEnabled(True)
            # self.control_panel.sheathflow_button.setEnabled(True)
            # self.control_panel.sampleflow_button.setEnabled(True)
            self.control_panel.probedialog_button.setEnabled(True)
            self.control_panel.clean_button.setEnabled(True)
            # self.control_panel.boost_button.setEnabled(True)
            self.control_panel.systemIDButton.setEnabled(True) #TODO: COMMENT THIS OUT AFTER TESTING

        self.control_panel.connect_button.setEnabled(True)

    def update_start(self):
        """!
        This function is called to enable the normal operation after user setting the probe.
        """
        self.control_panel.start_button.setEnabled(True)
        # self.control_panel.stop_button.setEnabled(True)
        self.control_panel.feedback_button.setEnabled(True) 
        self.control_panel.probedown_button.setEnabled(True)
        self.control_panel.sheathflow_button.setEnabled(True)
        self.control_panel.sampleflow_button.setEnabled(True)
        self.control_panel.systemIDButton.setEnabled(True)
            
    def command_input(self, user_input):
        """!
        This method is called anytime the user presses the Enter button, it reads the command_line
        QLineEdit and interprets that into a command

        ISSUE: there is not a defined expectation of parameters some have 0 or 1 or 2
        List of commands possible given Fluidics document:
        Command:                Parameters:                 Num Parameters:
        Start                   N/A                         0
        P                       1/0                         1
        SON                     #(int)                      1   -> sample  flow rate
        A                       N/A                         0
        VON                     1/2, number (int)           2
        SOFF                    N/A                         0
        PID                     1/2/3/4, KP/KI/KD           2
        SM                      x (int 1-16)                1
        SITL                    N/A                         0
        SITH                    N/A                         0
        QF                      N/A                         0
        RESTART                 # (?)                       1
        B                       N/A                         0
        BF                      N/A                         0 
        BW                      N/A                         0
        J                       # (num)                     1
        ST                      # (num)                     1
        F                       # (num)                     1   -> sheath flow rate
        """
        ##NOTE: user_input is expected to be a string...
        user_input = user_input.split()
        if user_input[0] == "START":
            self.processor.send_command(user_input[0])
        elif user_input[0] == "A":
            self.processor.send_command(user_input[0])
        elif user_input[0] == "RESTART":
            self.processor.send_command(user_input[0])
        elif user_input[0] == "B":
            self.processor.send_command(user_input[0])
        elif user_input[0] == "BF":
            self.processor.send_command(user_input[0])
        elif user_input[0] == "SITH":
            self.processor.send_command(user_input[0])
            # self.processor.send_command("RESTART")
        elif user_input[0] == "SITL":
            self.processor.send_command(user_input[0] + " " + user_input[1])
            # self.processor.send_command("RESTART")
        elif user_input[0] == "P":
            if self.control_panel.pidcontrol_status.state == 0:
                self.processor.send_command(str(user_input[0] + " 1"))
            elif self.control_panel.pidcontrol_status.state == 1:
                self.processor.send_command(str(user_input[0] + " 0"))
            else:
                print("This is not a real (possible) condition if we get here INVESTIGATE!")
        elif user_input[0] == "BOOST":
            if self.control_panel.boost_status.state == 0:
                self.processor.send_command(str(user_input[0] + " 1"))
            elif self.control_panel.boost_status.state == 1:
                self.processor.send_command(str(user_input[0] + " 0"))
            else:
                print("This is not a real (possible) condition if we get here INVESTIGATE!")
        elif user_input[0] == "SON":
            if 15 <= float(user_input[1]) <= 80:
                self.processor.send_command(str(user_input[0] + " " + user_input[1]))
                self.control_panel.boost_button.setEnabled(True)
            elif 0 <= float(user_input[1]) < 15:
                self.processor.send_command(str('SITL 0'))
                self.processor.send_command(str('SOFF'))
                self.control_panel.boost_button.setEnabled(False)
            else:
                self.control_panel.command_output.append("> Error: sample flow rate out of range 0-80")
        elif user_input[0] == "F":
            if 0 <= float(user_input[1]) <= 5.5:
                self.processor.send_command(str(user_input[0] + " " + user_input[1]))
            else:
                self.control_panel.command_output.append("> Error: sheath flow rate out of range 0-5.5")
        elif user_input[0] == "VON":
            if(len(user_input)):
                if float(user_input[1]) == 1 or float(user_input[1]) == 2:
                    self.processor.send_command(str(user_input[0] + " " + user_input[1] + " " + user_input[2]))
                else:
                    self.control_panel.command_output.append("> Error: VON only has 2 vaccum sources.")    
            else:
                self.control_panel.command_output.append("> Error: number of inputs for VON command")
        elif user_input[0] == "SOFF":
            self.processor.send_command(user_input)
        elif user_input[0] == "PID":
            if 0 < int(user_input[1]) <= 4:
                if user_input[2] in ('KP', 'KI', 'KD'):
                    self.processor.send_command(user_input)
                else:
                    self.control_panel.command_output.append("> Error: PID only has 3 optional parameters, KP, KI, KD.")    
            else:
                self.control_panel.command_output.append("> Error: PID only has 4 controls 1-4.")    
        elif user_input[0] == "QF":
            self.processor.send_command(user_input[0])
        elif user_input[0] == "BW":
            self.processor.send_command(user_input[0])
        elif user_input[0] == "ST":
            self.processor.send_command(user_input[0] + user_input[1])
            if int(user_input[1]) == 1:
                print("Here!\r\n")
        elif user_input[0] == "J":
            print("sending j")
            print(user_input)
            
            if 0 < float(user_input[1]) <= 100:
                self.processor.send_command(str(user_input[0] + " " + user_input[1]))
            else:
                self.control_panel.command_output.append("> Error: J only has a float range from 1 - 100.")         

        elif user_input[0] == "VH":
            self.processor.send_command(user_input[0])

        elif user_input[0] == "SM":
            self.processor.send_command(user_input[0] + " " + user_input[1])

        elif user_input[0] == "VALVE":
            self.processor.send_command(user_input[0] + " " + user_input[1] + " " + user_input[2])

        #NOTE:  This is setup with no restrictions to allow fluidics easier options to update their 
        #       commands
        else:
            string = ""
            for x in user_input:
                string += (x + " ")
            self.processor.send_command(string)
            
    def prob_menu(self):
        """Creates a dropdown menu for selecting specific probe down commands."""
        menu = QMenu()

        # Define the commands and labels for the dropdown menu
        commands = [
            ("Top", "SITL 0"),
            ("75mL Tube", "SITL 1"),
            ("Above Plate", "SITL 2"),
            ("Inside Plate", "SITL 3")
        ]

        for label, command in commands:
            action = QAction(label, self.control_panel.probedown_button)
            action.triggered.connect(lambda _, cmd=command: self.command_input(cmd))
            menu.addAction(action)
        button_pos = self.control_panel.probedown_button.mapToGlobal(QPoint(0, self.control_panel.probedown_button.height()))
        menu.exec(button_pos)

    def send_commands_with_sitl(self, command):
        """Sends SITL 1 followed by the given command if the number is greater than 15."""
        # Extract the number from the SON command
        if command.startswith("SON"):
            try:
                number = int(command.split()[1])
                if number >= 15:
                    self.command_input("SITL 1")
            except (IndexError, ValueError):
                # Handle the case where the command does not have the expected format
                print("Invalid SON command format.")
        self.command_input(command)
    
    def send_commands_with_sitH(self, command):
        """Sends SITL 1 followed by the given command if the number is greater than 15."""
        # Extract the number from the SON command
        if command.startswith("A"):
            try:
                number = int(command.split()[1])
                if number >= 15:
                    self.command_input("SITL 1")
            except (IndexError, ValueError):
                # Handle the case where the command does not have the expected format
                print("Invalid SON command format.")
        self.command_input(command)

    #Function for running system ID
    #Needs to 
    def StartSystemIDMap(self):
        #Vacuum Level:
        vacuumLevel = -3.0 #Just for testing
        degassVaccumLevel = -1.0
        #Delays
        homeDelay = 3 #In seconds
        stepDelay = 0.1 #Time between steps

        maxPosInput = 45000 #Defined in the firmware of the device
        minPosInput = 0 #Home
        #Vars for starting position
        startPosWindowTitle = "Please enter starting position for system ID"
        startPosMainText = "Starting position"
        startPosInputBoxXSize = 500
        startPosInputBoxYSize = 500

        #Vars for ending position
        endingPosWindowTitle = "Please enter ending position for system ID"
        endingPosMainText = "Ending position"
        endingPosInputBoxXSize = 500
        endingPosInputBoxYSize = 500

        #Vars for step size pop up
        stepsSizeWindowTitle = "Please enter the step size"
        stepsSizeMainText = "Step Size"
        stepsSizeInputBoxXSize = 500
        stepsSizeInputBoxYSize = 500

        #Turn off the constant updating with the QF function
        self.processor.system_ID_running = True
        
        #Get total steps, check if it's an integer number, and that it's in range
        startingPos = self.control_panel.CreatePopUpBoxToAttainInputValues(startPosWindowTitle, startPosMainText, startPosInputBoxXSize, startPosInputBoxYSize)
        startingPos = self.control_panel.ConvertStrToInt(startingPos)
        if(startingPos == None or startingPos > maxPosInput or startingPos < 0): #Check to make sure it's an integer and in range
            self.processor.system_ID_running = False
            print("Aborting system ID test...")
            return

        #Get step size, check if it's an integer number, and that it's in range
        endingPos = self.control_panel.CreatePopUpBoxToAttainInputValues(endingPosWindowTitle, endingPosMainText, endingPosInputBoxXSize, endingPosInputBoxYSize)
        endingPos = self.control_panel.ConvertStrToInt(endingPos)
        if(endingPos == None or endingPos > maxPosInput or endingPos < 0): #Check to make sure it's an integer and in range
            self.processor.system_ID_running = False
            print("Aborting system ID test...")
            return

        #Total Distance in steps
        totalDistance = abs(endingPos - startingPos)
        
        #Get step size, check if it's an integer number, and that it's in range
        stepSize = self.control_panel.CreatePopUpBoxToAttainInputValues(stepsSizeWindowTitle, stepsSizeMainText, stepsSizeInputBoxXSize, stepsSizeInputBoxYSize)
        stepSize = self.control_panel.ConvertStrToInt(stepSize)
        if(stepSize == None or stepSize > totalDistance or stepSize < 0): #Check to make sure it's an integer and in range
            self.processor.system_ID_running = False
            print("Aborting system ID test...")
            return

        #Start a recording if they aren't recording already
        if not sharedFluidicsFileClass.buttonState:
            fileResponse = sharedFluidicsFileClass.StartStopRecording()
            if fileResponse == None:
                self.processor.system_ID_running = False
                return

        
        #Turn valves on / off
        self.command_input("VALVE 1 ON") #Turn on valve 1
        self.processor.ReadFluidicsResponse()
        self.command_input("VALVE 7 OFF") #Turn off valve 7 (Sample valve)
        self.processor.ReadFluidicsResponse()

        self.command_input("VH") #Home
        self.processor.ReadFluidicsResponse()
        sleep(homeDelay)  #time between sends #May need to change this or may not neeed it at all
        self.command_input(f"SM {startingPos}") #Go to starting position
        self.processor.ReadFluidicsResponse()
        print(f"Moving to position {startingPos}")

        self.command_input(f"VON 1 {vacuumLevel}")
        self.processor.ReadFluidicsResponse()
        self.command_input(f"VON 2 {degassVaccumLevel}") #Turn the degasser on
        self.processor.ReadFluidicsResponse()
        self.command_input("QF") #Get data
        qfValue = self.processor.ReadFluidicsResponse()
        qfValue = self.processor.ParseQFResponse(qfValue)
        self.processor.ReadFluidicsResponse()
        while float(qfValue[8]) > vacuumLevel:
            self.command_input("QF") #Get data
            qfValue = self.processor.ReadFluidicsResponse()
            qfValue = self.processor.ParseQFResponse(qfValue)
            if qfValue == None:
                print("There was no QF response...")
                break
            self.processor.ReadFluidicsResponse()
            print(f"Vacuum still building: {qfValue[8]}")

        #First assignment
        propValveStepsData = startingPos

        #Make steps and record the data along it
        for i in range(int(totalDistance / stepSize)): #Go to the step number requested with the step size requested            
            if startingPos > endingPos:
                self.command_input(f"SM -{stepSize}") #Go negative
                self.processor.ReadFluidicsResponse()
            else:
                self.command_input(f"SM {stepSize}") #Go positive
                self.processor.ReadFluidicsResponse()

            sleep(stepDelay)  #time between sends #May need to change this or may not neeed it at all
            self.command_input("QF") #Get data
            qfValue = self.processor.ReadFluidicsResponse()
            qfValue = self.processor.ParseQFResponse(qfValue)
            if qfValue == None:
                print("There was no QF response...")
                break
            self.processor.ReadFluidicsResponse()
            #Data sent over , commented out what isn't being sent. Subject to updates in the future
            sheathRateData = qfValue[0]
            sampleRateData = qfValue[1]
            #sampleState = qfValue[2]
            #PIDStatus = qfValue[3]
            #tubeDetected = qfValue[4]
            #sheathHighStatus = qfValue[5]
            #wasteLow = qfValue[6]
            #vacuumStatus = qfValue[7]
            vacuumData = qfValue[8]
            #boostStatus = qfValue[9]
            sampleVelocity = qfValue[10]
            sheathPumpStatus = int(qfValue[11])
            wastePumpStatus = int(qfValue[12])
            targetSampleData = qfValue[13]
            propValveStepsData = int(qfValue[14])
            sampleDerivativeData = qfValue[15]
            bubbleDetectedData = int(qfValue[16])
            #TODO: Hopefully these are in the correct order... Will have to check l8r s
            sharedFluidicsFileClass.append_data_to_file(sharedFluidicsFileClass.fileName, sharedFluidicsFileClass.get_timestamp() + "\t\t" + str(sampleVelocity) + "\t\t\t" +  str(sheathRateData) + "\t\t\t" +  str(sampleRateData) + "\t\t" + str(vacuumData) + "\t\t" + str(sheathPumpStatus) + "\t\t" + str(wastePumpStatus) + "\t\t" + str(targetSampleData) + "\t\t" + str(propValveStepsData) + "\t\t" + str(sampleDerivativeData) + "\t\t" + str(bubbleDetectedData) + '\n')
            stepPercent = format(((stepSize * i)/ totalDistance) * 100, ".2f")
            print(f"On step number {stepSize * i} of {totalDistance}, {stepPercent}% done")
            print(f"The sheath rate is {qfValue[0]}, the sample rate is {qfValue[1]}, and the vacuum level is {qfValue[8]}")

        #Stop the test
        sharedFluidicsFileClass.buttonState = 0 #Stop the recording
        self.command_input("VOFF 1") #Close the sample line #May be some weird issue here
        self.processor.ReadFluidicsResponse()
        self.command_input("VALVE 1 OFF") #Turn on valve 1
        self.processor.ReadFluidicsResponse()
        self.command_input("VALVE 7 ON") #Turn OFF valve 7 (Sample valve)
        self.processor.ReadFluidicsResponse()
        self.command_input("VH") #Home
        self.processor.ReadFluidicsResponse()
        self.processor.system_ID_running = False