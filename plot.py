import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QGridLayout
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QPainter, QPen, QColor, QFont
from Widgets import CircularProgressBar, FuelGauge
from Widgets import progress_bar
from Widgets import FuelGauge
import math

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.initData()
        self.initTimer()

    def initUI(self):
        # Main layout
        mainLayout = QGridLayout()
        self.setLayout(mainLayout)

        # Speed and RPM section
        speedRpmLayout = QHBoxLayout()
        speedRpmWidget = QWidget()
        mainLayout.addWidget(speedRpmWidget,0,0,1,3) ##########

        # Speed display
        speedLayout = QVBoxLayout()
        speedRpmLayout.addLayout(speedLayout)
        self.speedLabel = QLabel("Speed")
        self.speedBar = CircularProgressBar()
        self.speedBar.setBarColor(QColor(0, 200, 100))  # Green
        self.speedBar.setMaxValue(200)
        self.speedBar.setUnits("km/h")
        self.speedBar.setSize(400,400)
        self.speedBar.setFontsize(70)
        speedLayout.addWidget(self.speedLabel)
        speedLayout.addWidget(self.speedBar)

        # RPM display
        rpmLayout = QVBoxLayout()
        speedRpmLayout.addLayout(rpmLayout)
        self.rpmLabel = QLabel("RPM")
        self.rpmBar = CircularProgressBar()
        self.rpmBar.setBarColor(QColor(220, 50, 50))  # Red
        self.rpmBar.setMaxValue(6000)
        self.rpmBar.setUnits("RPM")
        self.rpmBar.setSize(200,200)
        self.rpmBar.setFontsize(20)
        rpmLayout.addWidget(self.rpmLabel)
        rpmLayout.addWidget(self.rpmBar)

        speedRpmWidget.setLayout(speedRpmLayout)

        # Fuel Gauge
        fuelGaugeLayout = QVBoxLayout()
        self.fuel_gauge = FuelGauge(self)
        speedRpmLayout.addLayout(fuelGaugeLayout)

        # Progress bars
        progressLayout = QHBoxLayout()

        self.batteryBar = progress_bar(self)
        self.batteryBar.progressBar("Battery")
        progressLayout.addWidget(self.batteryBar)

        progresslayout = QWidget()
        progresslayout.setLayout(progressLayout)

        mainLayout.addWidget(progresslayout, 1, 0, 1, 1, Qt.AlignTop)

        # Status Label
        self.statusLabel = QLabel("Status: Running")
        mainLayout.addWidget(self.statusLabel, 2, 0)
        self.statusLabel.setAlignment(Qt.AlignCenter)
        self.statusLabel.setStyleSheet("font-size: 16px; color: green;")

        mainLayout.setRowStretch(0, 1)  # Give top row more stretch
        mainLayout.setRowStretch(1, 0)
        mainLayout.setRowStretch(2, 0)
        mainLayout.setColumnStretch(0, 1)  # Let first column stretch
        mainLayout.setColumnStretch(1, 0)  # Second column less stretch?

        # Window properties
        self.setWindowTitle('Dashboard')
        self.setGeometry(0, 0, 1280, 720)
        self.show()

    def initData(self):
        # Initial data values
        self.speed = 0
        self.rpm = 0
        self.fuel = 100
        self.battery = 100

    def initTimer(self):
        # Timer for updating data
        self.timer = QTimer()
        self.timer.setInterval(100)  # Update every second
        self.timer.timeout.connect(self.updateData)
        self.fuel_change = -5
        self.timer.start()

    def updateData(self):
        # Simulate data changes
        self.speed += 1
        self.rpm += 100
        self.battery -= 3

        # Clamp values to reasonable ranges
        self.speed = min(self.speed, 200)  # Max speed 200 km/h
        self.rpm = min(self.rpm, 6000)    # Max RPM 6000   # Min fuel 0
        self.battery = max(self.battery, 0)  # Min battery 0

        # Update display
        self.speedBar.setValue(self.speed)
        self.rpmBar.setValue(self.rpm)
        self.batteryBar.setValue(self.battery)

        self.fuel_gauge.set_fuel_level(self.fuel_gauge.fuel_level + self.fuel_change)
        if self.fuel_gauge.fuel_level > 95:
            self.fuel_change = -1
        elif self.fuel_gauge.fuel_level < 5:
            self.fuel_change = 1

        if self.fuel < 20:
            self.statusLabel.setText("Status: Low Fuel")
            self.statusLabel.setStyleSheet("color: red;")
        elif self.battery < 15:
            self.statusLabel.setText("Status: Low Battery")
            self.statusLabel.setStyleSheet("color: red;")
        else:
            self.statusLabel.setText("Status: Running")
            self.statusLabel.setStyleSheet("color: green;")



if __name__ == '__main__':
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    sys.exit(app.exec_())
