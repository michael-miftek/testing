import sys
from PyQt6.QtWidgets import QMainWindow, QApplication, QMdiArea, QMdiSubWindow, QTextEdit
from PyQt6.QtGui import QAction

class MainWindow(QMainWindow):
    count = 0

    def __init__(self):
        super().__init__()
        self.mdi = QMdiArea()
        self.setCentralWidget(self.mdi)
        bar = self.menuBar()

        file = bar.addMenu("File [Click Here!]")
        file.addAction("New")
        file.addAction("Cascade")
        file.addAction("Tiled")
        file.triggered[QAction].connect(self.windowaction)
        self.setWindowTitle("Multi Document Interface")

    def windowaction(self, q):
        print("Triggered")

        if q.text() == "New":
            MainWindow.count += 1
            sub = QMdiSubWindow()
            sub.setWidget(QTextEdit())
            sub.setWindowTitle(f"subwindow{MainWindow.count}")
            self.mdi.addSubWindow(sub)
            sub.show()

        if q.text() == "Cascade":
            self.mdi.cascadeSubWindows()

        if q.text() == "Tiled":
            self.mdi.tileSubWindows()
def main():
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()