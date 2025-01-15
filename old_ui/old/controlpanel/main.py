import os
import sys

#NOTE:  This is done since the main call is not at the root of the project
sys.path.append("../..")
from service.autotrigger.autotrigger import AutoTriggerProcessor
from service.controller.controller import Controller
from service.mainboard.mainboardprocessor import MainboardProcessor
from controlpanel import ControlPanel

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from controlpanel import ControlPanel

"""
This file will call and setup the control panel in its own GUI to be used
"""

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__() 

        self.mainboard_processor = None
        self.controller = None
        self.autotrigger_processor = None
        
        self.mainboard_processor_thread = None
        self.autotrigger_processor_thread = None
        self.controller_thread = None
        
        self.setup_processors()

        self.controlpanel_view = ControlPanel(self.mainboard_processor, self.controller, self.autotrigger_processor)
        self.setCentralWidget(self.controlpanel_view)
        
        app.aboutToQuit.connect(self.clean_up)

        self.setWindowTitle("ControlPanel Service")
        
    def setup_processors(self):
        self.mainboard_processor = MainboardProcessor()
        self.mainboard_processor_thread = QThread()
        self.mainboard_processor.moveToThread(self.mainboard_processor_thread)
        
        self.controller = Controller()
        self.controller_thread = QThread()
        self.controller.moveToThread(self.controller_thread)
        self.controller_thread.started.connect(self.controller.run)
        
        self.autotrigger_processor = AutoTriggerProcessor()
        self.autotrigger_processor_thread = QThread()
        self.autotrigger_processor.moveToThread(self.autotrigger_processor_thread)
        
        self.controller_thread.start()        
        
    def clean_up(self):
        print("Closing ControlPanel")
        if self.autotrigger_processor_thread:
            self.autotrigger_processor_thread.quit()
        if self.controller_thread:
            self.controller.finish()
            self.controller_thread.quit()
        if self.mainboard_processor_thread:
            self.mainboard_processor.finish()
            self.mainboard_processor_thread.quit()
            
        self.controlpanel_view.finish()
        print("ControlPanel Closed")
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('fusion')
    w = MainWindow()
    w.show()
    app.exec()