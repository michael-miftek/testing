import sys

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout


class MyApp(QWidget):

    def __init__(self):
        super().__init__()

        self.text_label = QLabel()
        self.text_label.setText("Hello World!")
        self.text_label.setFont(QFont('Arial', 20))
        
        self.text_label1 = QLabel()
        self.text_label1.setText("New World!")
        self.text_label1.setFont(QFont('Arial', 20))

        self.button = QPushButton("Fancy Button")
        self.button.setFont(QFont('Arial', 14))
        self.button.clicked.connect(lambda: self.text_label.setText("Changed!"))
        
        self.button1 = QPushButton("Fancy Button1")
        self.button1.setFont(QFont('Arial', 14))
        self.button1.clicked.connect(lambda: self.text_label1.setText("Changed again!"))

        self.setGeometry(50, 50, 300, 200)
        self.setWindowTitle("PyQt6 Example")

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.text_label)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.text_label1)
        self.layout.addWidget(self.button1)
        self.setLayout(self.layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    ex.show()
    sys.exit(app.exec())






"""from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication
import sys

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__()

    

if __name__ == "__main__":
    print(sys.argv)

    app = QApplication(sys.argv)
    w = MainWindow(app)
    w.show()
    sys.exit(app.exec())"""