from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout
)
from PyQt5.QtCore import Qt
import sys


class SplashScreen(QWidget):
    def __init__(self, logo_path, parent=None):
        super().__init__(parent)
        self.Layout = QVBoxLayout(self)
        self.Layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.Layout)
        try:
            self.pixmap = QPixmap(logo_path)
            if self.pixmap.isNull():
                raise FileNotFoundError(f"Logo file not found: {logo_path}")
            self.pixmap = self.pixmap.scaledToWidth(550, Qt.SmoothTransformation)
            self.label = QLabel(self)
            self.label.setPixmap(self.pixmap)
            self.Layout.addWidget(self.label)
        except Exception as e:
            print(f"Error loading logo: {e}")
            self.label = QLabel(self)
            self.label.setText("Error loading logo")

        self.Layout.addWidget(self.label)
        self.setStyleSheet("background-color: black;")
        self.show()

