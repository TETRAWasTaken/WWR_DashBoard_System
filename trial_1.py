import sys
import math
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QGridLayout, QProgressBar, QLabel, QFrame,
                             QSizePolicy) # Added QSizePolicy
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QPolygonF, QBrush
from PyQt5.QtCore import Qt, QTimer, QPointF, QRectF

# --- Configuration ---
UPDATE_INTERVAL_MS = 100  # How often to update the values (in milliseconds)
MAX_RPM = 8000
MAX_SPEED = 240
MAX_FUEL = 100
MAX_OIL_TEMP = 120
MAX_BATTERY_VOLTAGE = 15
MIN_BATTERY_VOLTAGE = 10

# --- Custom Dial Gauge Widget ---
class DialGauge(QWidget):
    """A custom widget to display a value as a dial gauge."""
    def __init__(self, title="Gauge", unit="Units", min_val=0, max_val=100, parent=None):
        super().__init__(parent)
        self.title = title
        self.unit = unit
        self.min_val = min_val
        self.max_val = max_val
        self._value = min_val
        self.setMinimumSize(200, 200) # Set a minimum size for the widget
        # Make the widget expandable but keep aspect ratio
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


    def setValue(self, value):
        """Sets the current value of the gauge."""
        # Clamp value within min/max range
        self._value = max(self.min_val, min(self.max_val, value))
        self.update() # Trigger a repaint

    def value(self):
        """Returns the current value."""
        return self._value

    # Added resizeEvent to maintain aspect ratio
    def resizeEvent(self, event):
        side = min(self.width(), self.height())
        if self.width() > self.height():
            self.setFixedWidth(side)
            self.setFixedHeight(side) # Adjust height to match width
        else:
             self.setFixedHeight(side)
             self.setFixedWidth(side) # Adjust width to match height
        super().resizeEvent(event)


    def paintEvent(self, event):
        """Handles the painting of the widget."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing) # Enable anti-aliasing for smooth graphics

        side = min(self.width(), self.height())
        # Center the drawing area
        painter.translate((self.width() - side) / 2, (self.height() - side) / 2)
        # Set coordinate system based on the smaller side
        painter.setWindow(-100, -100, 200, 200)

        # --- Draw background and outline ---
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QBrush(QColor(240, 240, 240))) # Light gray background
        painter.drawEllipse(-95, -95, 190, 190)

        # --- Draw Title ---
        painter.setPen(Qt.black)
        font = QFont('Arial', 10, QFont.Bold)
        painter.setFont(font)
        painter.drawText(-50, -80, 100, 20, Qt.AlignCenter, self.title)

        # --- Draw Ticks and Labels ---
        painter.setFont(QFont('Arial', 8))
        painter.setPen(QPen(Qt.black, 1))
        num_ticks = 10
        angle_range = 270 # Degrees (from -135 to +135)
        start_angle = 135

        for i in range(num_ticks + 1):
            angle = start_angle + (i * angle_range / num_ticks)
            rad = math.radians(angle)
            tick_val = self.min_val + (i * (self.max_val - self.min_val) / num_ticks)

            # Draw tick marks
            if i % 2 == 0: # Major tick
                len_tick = 10
                painter.setPen(QPen(Qt.black, 2))
                # Draw labels for major ticks
                x_label = 80 * math.cos(rad)
                y_label = 80 * math.sin(rad)
                painter.drawText(int(x_label)-15, int(y_label)-5, 30, 10, Qt.AlignCenter, str(int(tick_val)))
            else: # Minor tick
                len_tick = 5
                painter.setPen(QPen(Qt.darkGray, 1))

            x1 = 95 * math.cos(rad)
            y1 = 95 * math.sin(rad)
            x2 = (95 - len_tick) * math.cos(rad)
            y2 = (95 - len_tick) * math.sin(rad)
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        # --- Draw Needle ---
        # Avoid division by zero if min_val == max_val
        value_range = self.max_val - self.min_val
        value_ratio = 0
        if value_range > 0:
             value_ratio = (self._value - self.min_val) / value_range

        needle_angle = start_angle + (value_ratio * angle_range)
        needle_rad = math.radians(needle_angle)

        painter.setPen(QPen(Qt.red, 3))
        painter.setBrush(QBrush(Qt.red))

        # Define needle shape (triangle)
        needle = QPolygonF([
            QPointF(0, 0), # Center point
            QPointF(6 * math.cos(needle_rad + math.pi / 2), 6 * math.sin(needle_rad + math.pi / 2)), # Base left
            QPointF(85 * math.cos(needle_rad), 85 * math.sin(needle_rad)), # Tip
            QPointF(6 * math.cos(needle_rad - math.pi / 2), 6 * math.sin(needle_rad - math.pi / 2))  # Base right
        ])
        painter.drawPolygon(needle)

        # Draw center hub
        painter.setBrush(QBrush(Qt.darkGray))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(-5, -5, 10, 10)

        # --- Draw Current Value and Unit ---
        painter.setPen(Qt.black)
        font = QFont('Arial', 12, QFont.Bold)
        painter.setFont(font)
        # Format value based on whether it's integer or float implicitly
        value_str = f"{int(self._value)}" if self._value == int(self._value) else f"{self._value:.1f}"
        painter.drawText(-50, 50, 100, 20, Qt.AlignCenter, value_str)

        font = QFont('Arial', 8)
        painter.setFont(font)
        painter.drawText(-50, 70, 100, 20, Qt.AlignCenter, self.unit)


# --- Custom **Vertical** Fuel Gauge Widget ---
class FuelGauge(QWidget):
    """A custom widget to display fuel level as a **vertical** color-changing rectangle."""
    def __init__(self, min_val=0, max_val=100, parent=None):
        super().__init__(parent)
        self.min_val = min_val
        self.max_val = max_val
        self._value = max_val
        # Adjust minimum size for vertical orientation
        self.setMinimumHeight(150)
        self.setMinimumWidth(60)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding) # Fixed width, expanding height


    def setValue(self, value):
        """Sets the current fuel level."""
        self._value = max(self.min_val, min(self.max_val, value))
        self.update()

    def value(self):
        """Returns the current fuel level."""
        return self._value

    def paintEvent(self, event):
        """Handles the painting of the vertical fuel gauge."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Adjust rect for vertical layout and title at bottom
        rect = self.rect().adjusted(5, 5, -5, -25) # Leave space at bottom for title
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QBrush(QColor(220, 220, 220))) # Background fill
        painter.drawRect(rect)

        # Calculate fill height based on value
        value_range = self.max_val - self.min_val
        fill_ratio = 0
        if value_range > 0:
            fill_ratio = (self._value - self.min_val) / value_range

        fill_height = int(rect.height() * fill_ratio)
        # Fill from the bottom up
        fill_rect = QRectF(rect.left(), rect.bottom() - fill_height, rect.width(), fill_height)

        # Determine fill color based on level
        if fill_ratio > 0.5:
            fill_color = QColor(0, 180, 0) # Green
        elif fill_ratio > 0.2:
            fill_color = QColor(255, 190, 0) # Yellow
        else:
            fill_color = QColor(200, 0, 0) # Red

        painter.setBrush(QBrush(fill_color))
        painter.setPen(Qt.NoPen) # No border for the fill
        painter.drawRect(fill_rect)

        # Draw Title at the bottom
        painter.setPen(Qt.white) # Changed title color for dark background
        font = QFont('Arial', 8, QFont.Bold) # Smaller font for title
        painter.setFont(font)
        title_rect = QRectF(rect.left(), rect.bottom() + 5, rect.width(), 15)
        painter.drawText(title_rect, Qt.AlignCenter, "Fuel")

        # Draw Percentage Text inside the bar if there's space
        if fill_height > 20:
             painter.setPen(Qt.white if fill_ratio > 0.2 else Qt.black) # Contrast text
             font = QFont('Arial', 8, QFont.Bold)
             painter.setFont(font)
             # Center text within the filled part
             text_rect = QRectF(fill_rect.left(), fill_rect.top(), fill_rect.width(), fill_rect.height())
             painter.drawText(text_rect, Qt.AlignCenter, f"{int(self._value)}%")


# --- Main Dashboard Window ---
class DashboardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vehicle Dashboard")
        self.setGeometry(100, 100, 700, 400) # Adjusted initial size

        # --- Create Widgets ---
        self.rpm_gauge = DialGauge("RPM", "x1000", 0, MAX_RPM / 1000)
        self.speed_gauge = DialGauge("Speed", "km/h", 0, MAX_SPEED)
        self.fuel_gauge = FuelGauge(0, MAX_FUEL) # Now vertical

        self.oil_temp_bar = QProgressBar()
        self.oil_temp_bar.setRange(0, MAX_OIL_TEMP)
        self.oil_temp_bar.setFormat("Oil: %v °C")
        self.oil_temp_bar.setTextVisible(True)
        self.oil_temp_bar.setOrientation(Qt.Horizontal)
        self.oil_temp_bar.setFixedHeight(25) # Slightly smaller height

        self.battery_volt_bar = QProgressBar()
        self.battery_volt_bar.setRange(MIN_BATTERY_VOLTAGE * 10, MAX_BATTERY_VOLTAGE * 10) # Use integers for range
        self.battery_volt_bar.setFormat("Batt: %.1f V") # Custom format handled in update
        self.battery_volt_bar.setTextVisible(True)
        self.battery_volt_bar.setOrientation(Qt.Horizontal)
        self.battery_volt_bar.setFixedHeight(25) # Slightly smaller height

        # --- Layout ---
        central_widget = QWidget()
        # Use QGridLayout for more control over placement
        main_layout = QGridLayout(central_widget)

        # Add widgets to the grid
        # Row 0: Dials and Fuel Gauge
        main_layout.addWidget(self.rpm_gauge, 0, 0)       # Row 0, Col 0
        main_layout.addWidget(self.speed_gauge, 0, 1)     # Row 0, Col 1
        # Span fuel gauge across rows used by progress bars for alignment
        main_layout.addWidget(self.fuel_gauge, 0, 2, 3, 1) # Row 0, Col 2, Span 3 rows, 1 col

        # Row 1: Oil Temp Bar (below dials)
        main_layout.addWidget(QLabel("Oil Temp:"), 1, 0, Qt.AlignRight) # Align label right
        main_layout.addWidget(self.oil_temp_bar, 1, 1)    # Row 1, Col 1

        # Row 2: Battery Voltage Bar (below oil temp)
        main_layout.addWidget(QLabel("Battery:"), 2, 0, Qt.AlignRight) # Align label right
        main_layout.addWidget(self.battery_volt_bar, 2, 1) # Row 2, Col 1

        # Set column stretch factors - let dials expand, fix fuel gauge width
        main_layout.setColumnStretch(0, 1) # RPM column
        main_layout.setColumnStretch(1, 1) # Speed column
        main_layout.setColumnStretch(2, 0) # Fuel column (no stretch)

        # Set row stretch factors - let dials row expand
        main_layout.setRowStretch(0, 1) # Dials/Fuel row
        main_layout.setRowStretch(1, 0) # Oil Temp row
        main_layout.setRowStretch(2, 0) # Battery row

        self.setCentralWidget(central_widget)

        # --- Simulation Timer ---
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_values)
        self.timer.start(UPDATE_INTERVAL_MS)

        # --- Initial Values ---
        self._sim_rpm = 0
        self._sim_speed = 0
        self._sim_fuel = 85.0
        self._sim_oil_temp = 20.0
        self._sim_battery = 12.5
        self._rpm_direction = 1
        self._speed_direction = 1
        self._temp_direction = 1

        self.update_display() # Set initial display state

    def update_values(self):
        """Simulates changing vehicle data."""
        # Simulate RPM fluctuation
        self._sim_rpm += 50 * self._rpm_direction
        if self._sim_rpm >= MAX_RPM or self._sim_rpm <= 0:
            self._rpm_direction *= -1
            self._sim_rpm = max(0, min(MAX_RPM, self._sim_rpm)) # Clamp

        # Simulate Speed fluctuation (linked loosely to RPM)
        self._sim_speed += (2 * self._speed_direction * (self._sim_rpm / MAX_RPM + 0.1))
        if self._sim_speed >= MAX_SPEED or self._sim_speed <= 0:
             self._speed_direction *= -1
             self._sim_speed = max(0, min(MAX_SPEED, self._sim_speed)) # Clamp

        # Simulate Fuel consumption (gradual decrease)
        self._sim_fuel -= 0.05
        if self._sim_fuel < 0:
            self._sim_fuel = MAX_FUEL # Refuel :)

        # Simulate Oil Temperature change
        self._sim_oil_temp += 0.2 * self._temp_direction
        if self._sim_oil_temp > MAX_OIL_TEMP - 10 or self._sim_oil_temp < 30:
            self._temp_direction *= -1
        self._sim_oil_temp = max(20, min(MAX_OIL_TEMP, self._sim_oil_temp)) # Clamp

        # Simulate Battery Voltage fluctuation
        self._sim_battery += (0.02 * self._rpm_direction) # Slightly affected by RPM direction
        self._sim_battery = max(MIN_BATTERY_VOLTAGE, min(MAX_BATTERY_VOLTAGE, self._sim_battery)) # Clamp

        self.update_display()

    def update_display(self):
        """Updates all the dashboard widgets with current simulated values."""
        self.rpm_gauge.setValue(self._sim_rpm / 1000) # Scale RPM for display
        self.speed_gauge.setValue(self._sim_speed)
        self.fuel_gauge.setValue(self._sim_fuel)
        self.oil_temp_bar.setValue(int(self._sim_oil_temp))
        # Update battery bar value and text separately for float formatting
        self.battery_volt_bar.setValue(int(self._sim_battery * 10))
        self.battery_volt_bar.setFormat(f"Batt: {self._sim_battery:.1f} V")

    def closeEvent(self, event):
        """Stops the timer when the window is closed."""
        self.timer.stop()
        event.accept()


# --- Application Entry Point ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Apply a simple style sheet for better looks
    app.setStyleSheet("""
        QMainWindow {
            background-color: #333; /* Dark background */
        }
        QLabel {
            color: white;
            font-size: 10pt; /* Slightly smaller label font */
            padding-right: 5px; /* Add padding to right-aligned labels */
        }
        QProgressBar {
            border: 1px solid grey;
            border-radius: 5px;
            text-align: center;
            color: black; /* Text color inside the bar */
            background-color: #555; /* Background of the bar area */
            font-size: 9pt;
        }
        QProgressBar::chunk {
            background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #05B8CC, stop: 1 #1E90FF); /* Gradient chunk */
            border-radius: 3px;
            /* width: 10px; /* Width is less useful for horizontal */
            /* margin: 0.5px; */
        }
        /* Style for the custom Fuel Gauge Background */
        FuelGauge {
             background-color: transparent; /* Make background transparent */
        }
    """)
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec_())
