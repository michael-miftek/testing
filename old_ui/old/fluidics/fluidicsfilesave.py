#For file save
from datetime import datetime
from PyQt6.QtWidgets import QFileDialog

class FluidicsFile():
    #Start for file save
    def __init__(self):
        self.fileName = None        
        self.buttonState = 0

    def StartStopRecording(self, *args):
        self.buttonState = not self.buttonState
        if(self.buttonState): 
            self.fileName = self.save_file_dialog()
            fileState = self.write_data_to_file(self.fileName, "DD:HH:MM:SS:MSMS | Sample Velocity mm/s | Sheath rate ml/min | Sample Rate ul/min | Vacuum PSI | Sheath Pump | Waste Pump | Sample Target | Prop Valve Steps | Sample Derivative | Bubble Detected \n")
            if fileState == None:
                self.buttonState = not self.buttonState #Turn button back off
                return(None)
        return(1)


    
    def save_file_dialog(self):
        # Use QFileDialog to open the save file dialog
        file_name, _ = QFileDialog.getSaveFileName(
            parent=None,
            caption="Save File As",
            directory="",
            filter="Text Files (*.txt);;All files (*)"
        )
        return file_name

    def write_data_to_file(self, file_path, data):
        # Check if a file path was provided
        if file_path:
            # Open the file at the specified path in write mode
            with open(file_path, 'w') as file:
                # Write data to the file
                file.write(data)
            return(1)
        else:
            return(None)

    def append_data_to_file(self, file_path, data):
        # Check if a file path was provided
        if file_path:
            # Open the file at the specified path in write mode
            with open(file_path, 'a') as file:
                # Write data to the file
                file.write(data)

    # Function to get the current timestamp formatted with day, hour, seconds, and milliseconds
    def get_timestamp(self):
        now = datetime.now()
        formatted_time = now.strftime("%d:%H:%M:%S") + ':' + str(now.microsecond // 1000).zfill(3) + ": " 
        return formatted_time
    
sharedFluidicsFileClass = FluidicsFile()

#End for file save  