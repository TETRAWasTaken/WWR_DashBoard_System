from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, \
    QMessageBox

from Widgets import DialGauge, ThrottleBar
from Widgets import FuelGauge

# Global Variables
MAX_RPM = 15000
MAX_SPEED = 120
MAX_FUEL = 100

class Dashboard(QWidget):
    def __init__(self, logo_path = None):
        super().__init__()
        self.logo_path = logo_path

        self.initUI()
        self.calibrateAnimation()

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

        self.batteryVol = QLabel("")
        self.batterylabel = QLabel("Battery Vol.")
        datavaluelayout.addWidget(self.batterylabel, 0, 0)
        datavaluelayout.addWidget(self.batteryVol, 1, 0)
        self.batterylabel.setAlignment(Qt.AlignCenter)
        self.batteryVol.setAlignment(Qt.AlignCenter)
        self.batteryVol.setStyleSheet("font-size: 20px; color: White;")

        self.coolantTemp = QLabel("")
        self.coolantlabel = QLabel("Coolant Temp.")
        datavaluelayout.addWidget(self.coolantlabel, 0, 1)
        datavaluelayout.addWidget(self.coolantTemp, 1, 1)
        self.coolantlabel.setAlignment(Qt.AlignCenter)
        self.coolantTemp.setAlignment(Qt.AlignCenter)
        self.coolantTemp.setStyleSheet("font-size: 20px; color: White;")

        self.brakePressure = QLabel("")
        self.brakePressureLabel = QLabel("Brake Pressure")
        datavaluelayout.addWidget(self.brakePressureLabel, 0, 2)
        datavaluelayout.addWidget(self.brakePressure, 1, 2)
        self.brakePressureLabel.setAlignment(Qt.AlignCenter)
        self.brakePressure.setAlignment(Qt.AlignCenter)
        self.brakePressure.setStyleSheet("font-size: 20px; color: White;")

        self.oilLevel = QLabel("")
        self.oilLevelLabel = QLabel("Oil Level")
        datavaluelayout.addWidget(self.oilLevelLabel, 0, 3)
        datavaluelayout.addWidget(self.oilLevel, 1, 3)
        self.oilLevelLabel.setAlignment(Qt.AlignCenter)
        self.oilLevel.setAlignment(Qt.AlignCenter)
        self.oilLevel.setStyleSheet("font-size: 20px; color: White;")


        # Status Label
        self.statusLabel = QLabel("Status: Running")
        mainLayout.addWidget(self.statusLabel, 5, 1)
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
        
    def calibrateAnimation(self):
        self.batteryVol.setStyleSheet("font-size: 60px; color: White;")
        self.coolantTemp.setStyleSheet("font-size: 60px; color: White;")
        self.brakePressure.setStyleSheet("font-size: 60px; color: White;")
        self.oilLevel.setStyleSheet("font-size: 60px; color: White;")

        self.calibration_timer = QTimer()
        self.calibration_timer.setInterval(16)
        self.calibration_phase = 0
        self.calibration_value = 0
        self.gear = "N"
        self.count = 0

        def update_calibration():
            if self.calibration_phase == 0:  # Going up
                self.calibration_value += 1.6
                self.count += 1
                self.speed = round(self.calibration_value * MAX_SPEED / 100, 1)
                self.rpm = round(self.calibration_value * MAX_RPM / 100000, 1)
                self.throttle = round(self.calibration_value, 2)
                self.fuel = round(self.calibration_value, 2)
                self.batteryVolval = round(self.calibration_value / 10, 2)
                self.coolantTempval = round(self.calibration_value, 2)
                self.brakePressureval = round(self.calibration_value, 2)
                self.oilLevelval = round(self.calibration_value, 2)
                if self.count % 11 == 0:
                    self.gear = int(self.count // 11)
                self.updateData()
                if self.calibration_value >= 100:
                    self.calibration_phase = 1
            else:  # Going down
                self.calibration_value -= 1.6
                self.count -= 1
                self.speed = round(self.calibration_value * MAX_SPEED / 100, 1)
                self.rpm = round(self.calibration_value * MAX_RPM / 100000, 1)
                self.throttle = round(self.calibration_value, 2)
                self.fuel = round(self.calibration_value, 2)
                self.batteryVolval = round(self.calibration_value / 10, 2)
                self.coolantTempval = round(self.calibration_value, 2)
                self.brakePressureval = round(self.calibration_value, 2)
                self.oilLevelval = round(self.calibration_value, 2)
                if self.count % 11 == 0:
                    self.gear = int(self.count // 11)
                self.updateData()
                if self.calibration_value <= 0:
                    self.reset()
                    self.calibration_timer.stop()

        self.calibration_timer.timeout.connect(update_calibration)
        self.calibration_timer.start()

    def updateData(self):
        self.speed_dial.setValue(self.speed)
        self.rpm_dial.setValue(self.rpm)
        self.throttleBar.setValue(self.throttle)
        self.fuel_gauge.setValue(self.fuel)

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
        self.gearPosition.setText(str(self.gear))

    def reset(self):
        self.batteryVol.setStyleSheet("font-size: 20px; color: White;")
        self.coolantTemp.setStyleSheet("font-size: 20px; color: White;")
        self.brakePressure.setStyleSheet("font-size: 20px; color: White;")
        self.oilLevel.setStyleSheet("font-size: 20px; color: White;")

        self.batteryVol.setText("Loading...")
        self.coolantTemp.setText("Loading...")
        self.brakePressure.setText("Loading...")
        self.oilLevel.setText("Loading...")
        self.gearPosition.setText("N")


