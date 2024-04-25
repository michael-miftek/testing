"""import pytest
import pytestqt
from PyQt6 import QtCore

from PyQt6.QtWidgets import QLabel"""

#import maintest

"""@pytest.fixture
def app(qtbot):
    test_app = maintest.MainWindow()
    qtbot.addWidget(test_app)
    #qtbot.addWindow(test_app)

    return test_app"""

"""
# List Testing
listVar = []
listVar.append(0)
listVar.append(0)
print(f"var0: {listVar[0]}, var1: {listVar[1]}")

listVar[0] = 2
listVar[1] = 4

print(f"var0: {listVar[0]}, var1: {listVar[1]}")
listVar.pop(0)
print(f"var0: {listVar[0]}")"""


# def test_button_after_click(qtbot):
#     """qtbot.mouseClick(app.closeButton, QtCore.Qt.MouseButton.LeftButton)
#     assert app.button.isChecked() == True"""
#     window = maintest.MainWindow()
#     assert(window.close())
#     """
#     main_window = QMainWindow()
#     box = messageBoxFactory(main_window, "Informational Message", "Some information", level="info")
#     dialogButtonBox : QDialogButtonBox = box.children()[2]
#     okayBtn = dialogButtonBox.buttons()[0]
#     qtbot.mouseClick(okayBtn, Qt.LeftButton, Qt.NoModifier)
#     """


# This works for testing maybe want to talk about removing pytest
# import pytest
# import sys

# from PyQt6 import QtCore
# from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QApplication
# from PyQt6.QtGui import QFont
# from PyQt6.QtTest import QTest

# import maintest

# app = QApplication(sys.argv)
# mainApp = maintest.MyApp()
# assert(mainApp.text_label.text() == "Hello World!")
# QTest.mouseClick(mainApp.button, QtCore.Qt.MouseButton.LeftButton)
# assert(mainApp.text_label.text() == "Changed!")