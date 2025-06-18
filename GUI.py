import sys
import threading

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QGridLayout, \
    QMessageBox
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QPixmap
from Widgets import FuelGauge, DialGauge, ThrottleBar
from Widgets import progress_bar
from Widgets import FuelGauge
import math

# Global Variables
MAX_RPM = 6000
MAX_SPEED = 200
MAX_FUEL = 100

class Dashboard(QWidget):
    def __init__(self, logo_path = None):
        super().__init__()
        self.logo_path = logo_path

        self.initUI()
        self.initData()
        self.initTimer()

    def initUI(self):
        # Main layout
        mainLayout = QGridLayout()
        self.setLayout(mainLayout)

        # WWR Logo anf tagline
        miscellaneousLayout = QGridLayout()
        miscellaneousLayout.setSpacing(150)
        mainLayout.addLayout(miscellaneousLayout, 0, 0)

        try:
            self.logo = QLabel(self)
            pixmap = QPixmap(self.logo_path)
            pixmap = pixmap.scaledToWidth(150, Qt.SmoothTransformation)
            self.logo.setPixmap(pixmap)
            self.logo.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            miscellaneousLayout.addWidget(self.logo, 0, 0)

        except Exception as e:
            QMessageBox.critical(self, "Error", "Logo not found")

        tag = "Designed To Perform, Manufactured to Win"
        for i in range(20):
            tag = ' '+tag
        self.tagline = QLabel(tag)
        self.tagline.setAlignment(Qt.AlignCenter)
        self.tagline.setFont(QFont('Arial', 20, QFont.Bold))
        miscellaneousLayout.addWidget(self.tagline, 0, 1)

        # Speed and RPM section
        speedRpmLayout = QGridLayout()
        mainLayout.addLayout(speedRpmLayout, 1, 0, 1, 2)

        # Gear Display
        gearLayout = QGridLayout()
        self.gearPosition = QLabel('5')
        self.gearPositionLabel = QLabel('Gear')
        self.gearPosition.setAlignment(Qt.AlignCenter)
        self.gearPositionLabel.setAlignment(Qt.AlignCenter)
        gearLayout.addWidget(self.gearPositionLabel, 0, 0)
        gearLayout.addWidget(self.gearPosition, 1, 0, 2, 1)
        self.gearPosition.setStyleSheet("font-size: 200px; color: White;")
        gearLayout.setRowStretch(1, 1)
        speedRpmLayout.addLayout(gearLayout, 0, 1)

        # Speed display
        speedLayout = QVBoxLayout()
        speedRpmLayout.addLayout(speedLayout, 0, 0)
        self.speed_dial = DialGauge('Speed', 'KM/H', 0, MAX_SPEED, minx=450, miny=450)
        speedLayout.addWidget(self.speed_dial)

        # RPM display
        rpmLayout = QVBoxLayout()
        speedRpmLayout.addLayout(rpmLayout, 0, 2)
        self.rpm_dial = DialGauge('RPM', 'x1000', 0, MAX_RPM/1000, minx=400, miny=400)
        rpmLayout.addWidget(self.rpm_dial)

        # Fuel Gauge
        self.fuel_gauge = FuelGauge(0, MAX_FUEL)
        mainLayout.addWidget(self.fuel_gauge, 1, 2)

        # Progress bars
        self.throttleBar = ThrottleBar(self, min_val=0, max_val=MAX_FUEL)
        mainLayout.addWidget(self.throttleBar, 2, 0, 1, 2)

        # Data Values
        datavaluelayout = QGridLayout()
        mainLayout.addLayout(datavaluelayout, 4, 0, 1, 4)

        self.batteryVol = QLabel("Loading..")
        self.batterylabel = QLabel("Battery Vol.")
        datavaluelayout.addWidget(self.batterylabel, 0, 0)
        datavaluelayout.addWidget(self.batteryVol, 1, 0)
        self.batterylabel.setAlignment(Qt.AlignCenter)
        self.batteryVol.setAlignment(Qt.AlignCenter)
        self.batteryVol.setStyleSheet("font-size: 20px; color: White;")

        self.coolantTemp = QLabel("Loading..")
        self.coolantlabel = QLabel("Coolant Temp.")
        datavaluelayout.addWidget(self.coolantlabel, 0, 1)
        datavaluelayout.addWidget(self.coolantTemp, 1, 1)
        self.coolantlabel.setAlignment(Qt.AlignCenter)
        self.coolantTemp.setAlignment(Qt.AlignCenter)
        self.coolantTemp.setStyleSheet("font-size: 20px; color: White;")

        self.brakePressure = QLabel("Loading..")
        self.brakePressureLabel = QLabel("Brake Pressure")
        datavaluelayout.addWidget(self.brakePressureLabel, 0, 2)
        datavaluelayout.addWidget(self.brakePressure, 1, 2)
        self.brakePressureLabel.setAlignment(Qt.AlignCenter)
        self.brakePressure.setAlignment(Qt.AlignCenter)
        self.brakePressure.setStyleSheet("font-size: 20px; color: White;")

        self.oilLevel = QLabel("Loading..")
        self.oilLevelLabel = QLabel("Oil Level")
        datavaluelayout.addWidget(self.oilLevelLabel, 0, 3)
        datavaluelayout.addWidget(self.oilLevel, 1, 3)
        self.oilLevelLabel.setAlignment(Qt.AlignCenter)
        self.oilLevel.setAlignment(Qt.AlignCenter)
        self.oilLevel.setStyleSheet("font-size: 20px; color: White;")


        # Status Label
        self.statusLabel = QLabel("Status: Running")
        mainLayout.addWidget(self.statusLabel, 5, 0)
        self.statusLabel.setAlignment(Qt.AlignCenter)
        self.statusLabel.setStyleSheet("font-size: 20px; color: green;")

        # Row And Column STrech Adjusments
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
        mainLayout.setColumnStretch(2, 1)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)
        mainLayout.setRowStretch(3, 0)

        self.show()

    def initData(self):
        # Initial data values
        self.speed = 0
        self.rpm = 0
        self.fuel = 100
        self.throttle = 100
        self.batteryVolval = 0
        self.coolantTempval = 0
        self.brakePressureval = 0
        self.oilLevelval = 0

    def initTimer(self):
        # Timer for updating data
        self.batteryVol.setStyleSheet("font-size: 60px; color: White;")
        self.coolantTemp.setStyleSheet("font-size: 60px; color: White;")
        self.brakePressure.setStyleSheet("font-size: 60px; color: White;")
        self.oilLevel.setStyleSheet("font-size: 60px; color: White;")
        self.timer = QTimer()
        self.timer.setInterval(16)  # Update every second
        self.timer.timeout.connect(self.updateData)
        self.fuel_change = -5
        self.timer.start()

    def updateData(self):
        # Simulate data changes
        self.speed += 0.1
        self.rpm += 0.01
        self.throttle -= 0.05
        self.batteryVolval += 0.1
        self.coolantTempval += 0.1
        self.brakePressureval += 0.1
        self.oilLevelval += 0.1

        self.batteryVolval = round(self.batteryVolval,2)
        self.coolantTempval = round(self.coolantTempval,2)
        self.brakePressureval = round(self.brakePressureval,2)
        self.oilLevelval = round(self.oilLevelval,2)

        # Clamp values to reasonable ranges
        self.speed = min(self.speed, 200)
        self.rpm = min(self.rpm, MAX_RPM)
        self.throttle = max(self.throttle, 0)

        # Update display
        self.speed_dial.setValue(self.speed)
        self.rpm_dial.setValue(self.rpm)
        self.throttleBar.setValue(self.throttle)

        self.fuel_gauge.setValue(self.fuel_gauge.value() + self.fuel_change)
        if self.fuel_gauge.value() > 95:
            self.fuel_change = -1
        elif self.fuel_gauge.value() < 5:
            self.fuel_change = 1

        if self.fuel < 20:
            self.statusLabel.setText("Status: Low Fuel")
            self.statusLabel.setStyleSheet("color: red;")
        elif self.throttle < 15:
            self.statusLabel.setText("Status: Low Battery")
            self.statusLabel.setStyleSheet("color: red;")
        else:
            self.statusLabel.setText("Status: Running")
            self.statusLabel.setStyleSheet("color: green;")

        self.batteryVol.setText(str(self.batteryVolval) + " V")
        self.coolantTemp.setText(str(self.coolantTempval) + " C")
        self.brakePressure.setText(str(self.brakePressureval) + " kPa")
        self.oilLevel.setText(str(self.oilLevelval))

    def Tthread(self, start, end):
        range = (end - start)
        inc = range/60
        timer = threading.Thread(target=self.animator, args=(range, inc))
        timer.start()
        return timer

    def animator(self, range, inc):
        self.Timer = QTimer()
        self.Timer.setInterval(16)
        val = range + inc
        return val

    def WindowProperties(self):
        self.setWindowTitle('WWR')
        self.setGeometry(0, 0, 1280, 720)
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet("""
    QWidget {
        background-color: black; 
    }
    FuelGauge {
        background-color: black;
    } 
    """)
    dashboard = Dashboard()
    dashboard.WindowProperties()
    sys.exit(app.exec_())
