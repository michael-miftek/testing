from PyQt6 import QtCore
from PyQt6.QtWidgets import (QWidget, QDockWidget, QSpinBox, QSlider, QFormLayout, QHBoxLayout, 
                             QPushButton, QLabel)
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QPoint

class ProbeDialogWindow(QDockWidget):
    def __init__(self, control_panel):
        super().__init__("Probe Alignment")
        self.maxdepth = 10000
        self.control_panel = control_panel
        prbDialog = QWidget()
        self.setWidget(prbDialog) #NOTE: THIS IS A REQUIRED PATTERN
        hbox = QHBoxLayout()
        hbox.addStretch()
        self.sld = QSlider(QtCore.Qt.Orientation.Vertical)
        self.sld.setRange(0, self.maxdepth)
        self.sld.setValue(0)
        self.sld.setInvertedAppearance(True) 
        
        hbox.addWidget(self.sld)

        self.spinbox = QSpinBox()
        self.spinbox.setRange(0, self.maxdepth)
        self.spinbox.setValue(0)
        self.setDepth = QLabel()
        self.setButton = QPushButton("Move")
        self.lockButton = QPushButton("Set")

        self.setting_actual = 0
        self.setting_mm = 0

        formbox = QFormLayout()
        formbox.addRow("Probe Depth, step:", self.spinbox)
        formbox.addRow("Probe Depth, mm:", self.setDepth)
        formbox.addRow("Setting", self.setButton)
        formbox.addRow("Lock", self.lockButton)
        formbox.setVerticalSpacing(20)


        #hbox.addWidget(self.label)
        hbox.addStretch()
        hbox.addLayout(formbox)
        hbox.addStretch()

        prbDialog.setLayout(hbox)
        
        #hbox.addSpacerItem()
        #hbox.addWidget(sld)
        #self.groupbox.setLayout(hbox)
        self.setGeometry(300, 300, 350, 250)
        self.setFloating(True)

        # Lower probe

        self.sld.valueChanged.connect(self.sliderChanged)
        self.spinbox.valueChanged.connect(self.spinboxChanged)
        self.setButton.clicked.connect(lambda : self.control_panel.fluidics_processor.send_command(f"J {self.setting_mm}"))
        # self.lockButton.clicked.connect(lambda: self.control_panel.fluidics_processor.send_command(f"ST"))
        self.lockButton.clicked.connect(lambda: self.prob_menu())
        #if dialog closed before button clicked, return all values to current main
        #present probe height must always be updated

    def sliderChanged(self):
        newValue = int(self.sld.value())
        self.spinbox.setValue(newValue)
        self.setting_actual = newValue
        self.setting_mm = self.stepToHeight()
        self.setDepth.setText("{0:.5f}".format(self.setting_mm))


    def spinboxChanged(self): #slider
        newValue = int(self.spinbox.value())
        self.sld.setValue(newValue)
        self.setting_actual = newValue
        self.setting_mm = self.stepToHeight()
        self.setDepth.setText("{0:.5f}".format(self.setting_mm))

    def stepToHeight(self):
        return self.setting_actual / 100 
        # return (self.maxdepth-self.setting_actual)/100 
    
    def prob_menu(self):
        """Creates a dropdown menu for selecting specific probe down commands."""
        menu = QMenu()

        # Define the commands and labels for the dropdown menu
        commands = [
            ("Top", "ST 0"),
            ("75mL Tube", "ST 1"),
            ("Above Plate", "ST 2"),
            ("Inside Plate", "ST 3")
        ]

        for label, command in commands:
            action = QAction(label,self.lockButton)
            action.triggered.connect(lambda _, cmd=command: self.control_panel.fluidics_processor.send_command(cmd))
            menu.addAction(action)
        button_pos = self.lockButton.mapToGlobal(QPoint(0, self.lockButton.height()))
        menu.exec(button_pos)   