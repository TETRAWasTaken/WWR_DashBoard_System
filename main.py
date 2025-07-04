#!/usr/bin/env python3
import DashBoard as DashBoard
import SplashScreen as SplashScreen
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget
)
from PyQt5.QtCore import QTimer, Qt

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

class App(QMainWindow):
    def __init__(self, logo_path):
        super().__init__()
        try:
            self.setWindowTitle("Wrench Weilders Racing")
            self.setWindowFlag(Qt.FramelessWindowHint)
            self.setGeometry(0, 0, 800, 460)
            self.setFixedSize(800, 460)

            print("Initiating MainStack")

            self.mainStack = QStackedWidget()
            self.setCentralWidget(self.mainStack)

            print("Splash Screen Initiated")

            self.splashScreen = SplashScreen.SplashScreen(logo_path)
            self.mainStack.addWidget(self.splashScreen)

            self.mainStack.setCurrentIndex(0)

            self.dashboard = DashBoard.Dashboard(logo_path)
            self.mainStack.addWidget(self.dashboard)

            def switchStack():
                print("Dashboard Initiated")
                self.mainStack.setCurrentIndex(1)
                self.splashScreen.close()
                print("Running Calibration Animation")
                self.dashboard.calibrateAnimation()
                print("Calibration Animation Completed")
                print("Waiting For Sensory Input...")

            QTimer.singleShot(2500, switchStack)

        except Exception as e:
            print(f"Error loading dashboard: {e}")

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