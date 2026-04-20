#!/usr/bin/env python3
import threading

try:
    from . import DashBoard as DashBoard
    from . import SplashScreen as SplashScreen
except ImportError:
    import DashBoard as DashBoard
    import SplashScreen as SplashScreen
#from src.Data_Aq_Dist import mqtt_recv
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget
)
from PyQt5.QtCore import QTimer, Qt

#from src.Data_Aq_Dist.mqtt_recv import MQTT_Client

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

class App(QMainWindow):
    def __init__(self, logo_path):
        self.json = None
        super().__init__()
        try:
            self.setWindowTitle("Wrench Weilders Racing")
            self.setWindowFlag(Qt.FramelessWindowHint)
            self.setGeometry(0, 0, 800, 480)
            self.setFixedSize(800, 480)

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
                #self.data_aq()

            QTimer.singleShot(2500, switchStack)

        except Exception as e:
            print(f"Error loading dashboard: {e}")

    """
    def data_aq(self):
        self.mqtt_client = mqtt_recv.MQTT_Client("DashBoard")
        self.mqtt_client.start()
        while True:
            self.json = self.mqtt_client.get_message()
    """



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
    logo_path = "LOGO.jpeg"
    window = App(logo_path)
    window.show()
    sys.exit(app.exec_())