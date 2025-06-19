import DashBoard as DashBoard
import SplashScreen as SplashScreen
import sys
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QStackedWidget
)
from PyQt5.QtGui import QPixmap, QFont, QColor, QPainter # QPainter for drawing on QPixmap fallback
from PyQt5.QtCore import Qt, QTimer
import PyQt5.QtWidgets
import threading

class App(QMainWindow):
    def __init__(self, logo_path):
        super().__init__()
        self.setWindowTitle("Wrench Weilders Racing")
        self.setGeometry(0, 0, 1280, 720)
        self.setFixedSize(1280, 720)

        self.mainStack = QStackedWidget()
        self.setCentralWidget(self.mainStack)

        self.splashScreen = SplashScreen.SplashScreen(logo_path)
        self.mainStack.addWidget(self.splashScreen)

        self.mainStack.setCurrentIndex(0)

        self.dashboard = DashBoard.Dashboard(logo_path)
        self.mainStack.addWidget(self.dashboard)

        def switchStack():
            self.mainStack.setCurrentIndex(1)
            self.splashScreen.close()
            self.dashboard.calibrateAnimation()

        QTimer.singleShot(2500, switchStack)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    # Apply the stylesheet to the main application instance
    app.setStyleSheet("""
        QWidget {
            background-color: black; 
            color: #DAF1DE;
        }
        QLabel {
            background-color: transparent;
        }
    """)
    logo_path = "LOGO.png"
    window = App(logo_path)
    window.show()
    sys.exit(app.exec_())