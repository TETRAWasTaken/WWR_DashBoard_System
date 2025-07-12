from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, \
    QMessageBox

from Widgets import DialGauge
from Widgets import FuelGauge

# Global Variables
MAX_RPM = 15000
MAX_FUEL = 100

class Dashboard(QWidget):
    def __init__(self, logo_path = None):
        super().__init__()
        self.logo_path = logo_path

        self.initUI()
        self.calibrateAnimation()

    def initUI(self):
        self.setFixedSize(800, 480)

        # Main layout
        mainLayout = QGridLayout()
        self.setLayout(mainLayout)

        # WWR Logo anf tagline
        miscellaneousLayout = QGridLayout()
        miscellaneousLayout.setSpacing(30) # Reduced spacing
        mainLayout.addLayout(miscellaneousLayout, 0, 0)

        try:
            self.logo = QLabel(self)
            pixmap = QPixmap(self.logo_path)
            pixmap = pixmap.scaledToWidth(80, Qt.SmoothTransformation) # Reduced logo width
            self.logo.setPixmap(pixmap)
            self.logo.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            miscellaneousLayout.addWidget(self.logo, 0, 0)

        except Exception as e:
            QMessageBox.critical(self, "Error", "Logo not found")

        # Status Label
        self.statusLabel = QLabel("Status: Running")
        mainLayout.addWidget(self.statusLabel, 0, 1)
        self.statusLabel.setAlignment(Qt.AlignCenter)
        self.statusLabel.setFont(QFont('Arial', 20, QFont.Bold))  # Adjusted font size
        self.statusLabel.setStyleSheet("color: green;")

        # Gear and RPM section
        GearRpmLayout = QGridLayout()
        mainLayout.addLayout(GearRpmLayout, 1, 0, 1, 2)

        # Gear Display
        gearLayout = QGridLayout()
        self.gearPosition = QLabel('5')
        self.gearPositionLabel = QLabel('Gear')
        self.gearPosition.setAlignment(Qt.AlignCenter)
        self.gearPositionLabel.setAlignment(Qt.AlignCenter)
        gearLayout.addWidget(self.gearPositionLabel, 0, 0)
        gearLayout.addWidget(self.gearPosition, 1, 0)
        self.gearPosition.setStyleSheet("font-size: 160px; color: White;") # Reduced font size
        gearLayout.setRowStretch(1, 1)
        GearRpmLayout.addLayout(gearLayout, 0, 1)

        # RPM display
        rpmLayout = QVBoxLayout()
        GearRpmLayout.addLayout(rpmLayout, 0, 0)
        self.rpm_dial = DialGauge('RPM', 'x1000', 0, MAX_RPM/1000, minx=360, miny=360)
        rpmLayout.addWidget(self.rpm_dial)

        # Fuel Gauge
        self.fuel_gauge = FuelGauge(0, MAX_FUEL)
        mainLayout.addWidget(self.fuel_gauge, 1, 3)

        # Data Values
        datavaluelayout = QGridLayout()
        mainLayout.addLayout(datavaluelayout, 2, 1)

        self.coolantTemp = QLabel("")
        self.coolantlabel = QLabel("Coolant Temp.")
        datavaluelayout.addWidget(self.coolantlabel, 0, 1)
        datavaluelayout.addWidget(self.coolantTemp, 1, 1)
        self.coolantlabel.setAlignment(Qt.AlignCenter)
        self.coolantTemp.setAlignment(Qt.AlignCenter)
        self.coolantTemp.setStyleSheet("font-size: 16px; color: White;") # Adjusted to fit

        self.exhaustTemp = QLabel("")
        self.exhaustTempLabel = QLabel("Exhaust Temp")
        datavaluelayout.addWidget(self.exhaustTempLabel, 0, 2)
        datavaluelayout.addWidget(self.exhaustTemp, 1, 2)
        self.exhaustTempLabel.setAlignment(Qt.AlignCenter)
        self.exhaustTemp.setAlignment(Qt.AlignCenter)
        self.exhaustTemp.setStyleSheet("font-size: 16px; color: White;") # Adjusted to fit

        # Row And Column Strech Adjusments
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 7)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)

        self.show()
        
    def calibrateAnimation(self):
        # Adjusted font size for calibration animation
        self.coolantTemp.setStyleSheet("font-size: 30px; color: White;")
        self.exhaustTemp.setStyleSheet("font-size: 30px; color: White;")

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
                self.rpm = round(self.calibration_value * MAX_RPM / 100000, 1)
                self.fuel = round(self.calibration_value, 2)
                self.coolantTempval = round(self.calibration_value, 2)
                self.exhaustTempval = round(self.calibration_value, 2)
                self.oilLevelval = round(self.calibration_value, 2)
                if self.count % 11 == 0:
                    self.gear = int(self.count // 11)
                self.updateData()
                if self.calibration_value >= 100:
                    self.calibration_phase = 1
            else:  # Going down
                self.calibration_value -= 1.6
                self.count -= 1
                self.rpm = round(self.calibration_value * MAX_RPM / 100000, 1)
                self.fuel = round(self.calibration_value, 2)
                self.coolantTempval = round(self.calibration_value, 2)
                self.exhaustTempval = round(self.calibration_value, 2)
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
        self.rpm_dial.setValue(self.rpm)
        self.fuel_gauge.setValue(self.fuel)

        if self.fuel < 20:
            self.statusLabel.setText("Status: Low Fuel")
            self.statusLabel.setStyleSheet("color: red;")
        else:
            self.statusLabel.setText("Status: Running")
            self.statusLabel.setStyleSheet("color: green;")

        self.coolantTemp.setText(str(self.coolantTempval) + " C")
        self.exhaustTemp.setText(str(self.exhaustTempval) + " C")
        self.gearPosition.setText(str(self.gear))

    def reset(self):
        # Ensure reset font sizes are consistent with the new display
        self.coolantTemp.setStyleSheet("font-size: 16px; color: White;")
        self.exhaustTemp.setStyleSheet("font-size: 16px; color: White;")

        self.coolantTemp.setText("Loading...")
        self.exhaustTemp.setText("Loading...")
        self.gearPosition.setText("N")