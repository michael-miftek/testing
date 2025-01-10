import os
import sys
#NOTE:  This is done since the main call is not at the root of the project
sys.path.append("../..")

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

# from fluidics import FluidicsControlPanel
# from service.fluidics.fluidics_processor import FluidicsProcessor

"""
This file will call and setup the fluidics control panel  in its own GUI to be used
"""
#NOTE: This is only to be used to make sure that everything works as expected
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__() 

        # self.fluidics_processor = FluidicsProcessor()
        # self.fluidics_processor_thread = QThread()
        # self.fluidics_processor.moveToThread(self.fluidics_processor_thread)
        
        # self.fluidics_view = FluidicsControlPanel(self.fluidics_processor)
        # self.setCentralWidget(self.fluidics_view)
        self.setWindowTitle("Graphs testing")
        
        app.aboutToQuit.connect(self.clean_up)
        
    def clean_up(self):
        print("Graphs Fluidics")
        # self.fluidics_processor.close_connection()
        # self.fluidics_processor_thread.quit()
        # self.fluidics_view.finish()
        print("Graphs Closed")
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('fusion')
    w = MainWindow()
    w.show()
    app.exec()