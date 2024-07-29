from PyQt6 import QtCore, QtWidgets
from functools import partial


class SequentialManager(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    resultsChanged = QtCore.pyqtSignal(QtCore.QByteArray)

    def __init__(self, parent=None):
        super(SequentialManager, self).__init__(parent)
        self.process = QtCore.QProcess(self)
        self.process.finished.connect(self.handleFinished)
        self.process.readyReadStandardOutput.connect(self.onReadyReadStandardOutput)

    def start(self, commands):
        self._commands = iter(commands)
        print("Hi")
        self.fetchNext()

    def fetchNext(self):
        try:
            command = next(self._commands)
        except StopIteration:
            return False
        else:
            self.process.start(command)
        return True

    def onReadyReadStandardOutput(self):
        result = self.process.readAllStandardOutput()
        self.resultsChanged.emit(result)

    def handleFinished(self):
        if not self.fetchNext():
            self.finished.emit()


class Widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)
        vlay = QtWidgets.QVBoxLayout(self)
        self.te = QtWidgets.QTextEdit()
        self.te.setReadOnly(True)
        btn = QtWidgets.QPushButton("Start processes")
        vlay.addWidget(self.te)
        vlay.addWidget(btn)

        manager = SequentialManager(self)
        manager.resultsChanged.connect(self.onResultsChanged)

        commands = ["test1.cmd", "test2.cmd"]
        btn.clicked.connect(partial(manager.start, commands))

    def onResultsChanged(self, result):
        self.te.append(str(result, "utf-8"))


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = Widget()
    w.show()
    sys.exit(app.exec())

