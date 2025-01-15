import sys
from PyQt6.QtCore import Qt, QPoint, QRect, QSize
from PyQt6.QtGui import QCursor, QResizeEvent
from PyQt6.QtWidgets import QApplication, QWidget, QScrollArea, QVBoxLayout, QLabel

class ResizableWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumSize(100, 100)
        self.setCursor(QCursor(Qt.CursorShape.SizeFDiagCursor))
        self.resize_mode = False
        self.start_pos = None
        self.start_size = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.resize_mode = True
            self.start_pos = event.globalPosition()
            self.start_size = self.size()

    def mouseMoveEvent(self, event):
        if self.resize_mode:
            delta = event.globalPosition() - self.start_pos
            new_width = self.start_size.width() + delta.x()
            new_height = self.start_size.height() + delta.y()
            new_size = QSize(int(new_width), int(new_height))
            self.setFixedSize(new_size)

    def mouseReleaseEvent(self, event):
        self.resize_mode = False

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        scroll_area = QScrollArea(self)
        layout.addWidget(scroll_area)

        resizable_widget = ResizableWidget(scroll_area)
        resizable_widget.setStyleSheet("background-color: lightblue;")
        resizable_widget.setLayout(QVBoxLayout())
        label = QLabel("Drag to resize", resizable_widget)
        resizable_widget.layout().addWidget(label)

        scroll_area.setWidget(resizable_widget)
        scroll_area.setWidgetResizable(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())