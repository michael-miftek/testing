"""
Very simple example demonstrating RemoteGraphicsView.

This allows graphics to be rendered in a child process and displayed in the 
parent, which can improve CPU usage on multi-core processors.
"""
'''
import pyqtgraph as pg
from pyqtgraph.widgets.RemoteGraphicsView import RemoteGraphicsView
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QMainWindow, QTabWidget

app = pg.mkQApp()

## Create the widget
v = RemoteGraphicsView(debug=False)  # setting debug=True causes both processes to print information
                                    # about interprocess communication
v.show()
v.setWindowTitle('pyqtgraph example: RemoteGraphicsView')

## v.pg is a proxy to the remote process' pyqtgraph module. All attribute 
## requests and function calls made with this object are forwarded to the
## remote process and executed there. See pyqtgraph.multiprocess.remoteproxy
## for more inormation.
plt = v.pg.PlotItem()
v.setCentralItem(plt)
plt.plot([1,4,2,3,6,2,3,4,2,3], pen='g')

if __name__ == '__main__':
    pg.exec()
'''
'''
    Lets try and test this with drawing squares to make sure that contsant data can be used
'''

import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setCentralWidget(QtWidgets.QCheckBox())
        self.show()
        self.foo = Foo()

class Foo(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.rgfxview = pg.RemoteGraphicsView(debug=False)

        layout = QtWidgets.QVBoxLayout()
        self.button = QtWidgets.QCheckBox()
        layout.addWidget(self.button)
        layout.addWidget(self.rgfxview)
        self.setLayout(layout)

        self.rplt = self.rgfxview.pg.PlotItem() 
        self.rgfxview.setCentralItem(self.rplt)
        self.rplt.plot([1, 2, 3, 4, 5])

        self.show()

pg.mkQApp()
main = MainWindow()
pg.exec()