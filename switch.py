from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, QRect
import sys

class MySwitch(QtWidgets.QPushButton):
    def __init__(self, parent = None):
        super().__init__(parent)
        print('init')
        self.setCheckable(True)
        self.setMinimumWidth(66)
        self.setMinimumHeight(22)

    def paintEvent(self, event):
        label = "ON" if self.isChecked() else "OFF"
        bg_color = QtGui.QColor("green") if self.isChecked() else QtGui.QColor("red")

        radius = 10
        width = 32
        center = self.rect().center()

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
        painter.translate(center)
        painter.setBrush(QtGui.QColor(0,0,0))

        pen = QtGui.QPen(QtGui.QColor("black"))
        pen.setWidth(2)
        painter.setPen(pen)

        painter.drawRoundedRect(QRect(-width, -radius, 2*width, 2*radius), radius, radius)
        painter.setBrush(QtGui.QBrush(bg_color))
        sw_rect = QRect(-radius, -radius, width + radius, 2*radius)
        if not self.isChecked():
            sw_rect.moveLeft(-width)
        painter.drawRoundedRect(sw_rect, radius, radius)
        painter.drawText(sw_rect, QtCore.Qt.AlignmentFlag.AlignCenter, label)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        self.tableWidget.setColumnCount(4)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)

    def retranslateUi(self, MainWindow):
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "status"))

    def bindSave(self):
        ...
        ch_bx3 = MySwitch()
        ch_bx3.setChecked(True)
        ch_bx3.clicked.connect(ch_bx1.setEnabled)
        ch_bx3.clicked.connect(ch_bx2.setEnabled)
        self.tableWidget.setCellWidget(numRows, 3, ch_bx3)


if __name__ == "__main__":
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    MainWindow = QtWidgets.QMainWindow()
    ui        = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    app.exec()