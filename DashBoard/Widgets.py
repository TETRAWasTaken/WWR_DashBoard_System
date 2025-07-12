import math
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QBrush, QPolygonF
from PyQt5.QtWidgets import QWidget, QSizePolicy


class DialGauge(QWidget):
    """A custom widget to display a value as a dial gauge."""
    def __init__(self, title="Gauge", unit="Units", min_val=0, max_val=100, parent=None, minx=100, miny=100):
        super().__init__(parent)
        self.title = title
        self.unit = unit
        self.min_val = min_val
        self.max_val = max_val
        self._value = min_val
        self.setMinimumSize(minx, miny) # Set a minimum size for the widget
        # Make the widget expandable but keep aspect ratio
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


    def setValue(self, value):
        self._value = max(self.min_val, min(self.max_val, value))
        self.update() # Trigger a repaint

    def value(self):
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
        font = QFont('Arial', 18, QFont.Bold)
        painter.setFont(font)
        # Format value based on whether it's integer or float implicitly
        value_str = f"{int(self._value)}" if self._value == int(self._value) else f"{self._value:.1f}"
        painter.drawText(-50, 50, 100, 20, Qt.AlignCenter, value_str)

        font = QFont('Arial', 8)
        painter.setFont(font)
        painter.drawText(-50, 70, 100, 20, Qt.AlignCenter, self.unit)

class FuelGauge(QWidget):
    """A custom widget to display fuel level as a **vertical** color-changing rectangle."""
    def __init__(self, min_val=0, max_val=100, parent=None):
        super().__init__(parent)
        self.min_val = min_val
        self.max_val = max_val
        self._value = max_val
        # Adjust minimum size for vertical orientation
        self.setMinimumWidth(50)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding) # Fixed width, expanding height


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
        font = QFont('Arial', 12, QFont.Bold) # Smaller font for title
        painter.setFont(font)
        title_rect = QRectF(rect.left(), rect.bottom() + 5, rect.width(), 15)
        painter.drawText(title_rect, Qt.AlignCenter, "Fuel")

        # Draw Percentage Text inside the bar if there's space
        if fill_height > 20:
             painter.setPen(Qt.white if fill_ratio > 0.2 else Qt.black) # Contrast text
             font = QFont('Arial', 10, QFont.Bold)
             painter.setFont(font)
             # Center text within the filled part
             text_rect = QRectF(fill_rect.left(), fill_rect.top(), fill_rect.width(), fill_rect.height())
             painter.drawText(text_rect, Qt.AlignCenter, f"{int(self._value)}%")


class ThrottleBar(QWidget):
    def __init__(self, parent = None, min_val=0, max_val=100):
        super().__init__(parent)
        self.min_val = min_val
        self.max_val = max_val
        self._value = min_val # Start at minimum throttle
        self.title = "Throttle"

        # Adjust minimum size and size policy for horizontal orientation
        self.setMinimumHeight(40) # Reasonable minimum height
        self.setMinimumWidth(150) # Reasonable minimum width
        # Expand horizontally, keep height as preferred/minimum
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # If you want height to be flexible too use:
        # self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

    def setValue(self, value):
        """Sets the current throttle level."""
        self._value = max(self.min_val, min(self.max_val, value))
        self.update() # Trigger a repaint

    def value(self):
        """Returns the current throttle level."""
        return self._value

    def setTitle(self, title):
        """Sets the title text displayed below the bar."""
        self.title = title
        self.update()

    def paintEvent(self, event):
        """Handles the painting of the horizontal throttle bar."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Adjust rect for horizontal layout and title at bottom
        # Leave space: 5px left/top/right, 20px bottom for title
        rect = self.rect().adjusted(5, 5, -5, -20)
        if not rect.isValid(): # Don't draw if rect is invalid (e.g., too small)
             return

        # Draw Background
        painter.setPen(QPen(Qt.black, 1)) # Thinner pen
        painter.setBrush(QBrush(QColor(220, 220, 220))) # Background fill
        painter.drawRoundedRect(rect, 5, 5) # Use rounded corners

        # Calculate fill width based on value
        value_range = self.max_val - self.min_val
        fill_ratio = 0
        if value_range > 0:
            # Ensure value is within range for ratio calculation
            current_val_in_range = self._value - self.min_val
            fill_ratio = current_val_in_range / value_range

        fill_width = int(rect.width() * fill_ratio)

        # Create the fill rectangle - starting from the left
        # Ensure fill_width is not negative
        if fill_width > 0:
            fill_rect = QRectF(rect.left(), rect.top(), fill_width, rect.height())

            # Determine fill color based on level (Reversed logic for throttle)
            if fill_ratio < 0.5: # Low throttle
                fill_color = QColor(0, 180, 0) # Green
            elif fill_ratio < 0.8: # Mid throttle
                fill_color = QColor(255, 190, 0) # Yellow
            else: # High throttle
                fill_color = QColor(200, 0, 0) # Red

            painter.setBrush(QBrush(fill_color))
            painter.setPen(Qt.NoPen) # No border for the fill
            painter.drawRoundedRect(fill_rect, 5, 5) # Draw filled part with rounded corners

            # Draw Percentage Text inside the bar if there's space
            # Use fill_rect's dimensions for centering text
            if fill_width > 30: # Need enough width for text
                 # Choose text color for contrast
                 text_color = Qt.white if fill_ratio < 0.8 else Qt.black # White on Green/Yellow, Black on Red
                 painter.setPen(text_color)
                 font = QFont('Arial', 8, QFont.Bold)
                 painter.setFont(font)
                 # Center text vertically and horizontally within the filled part
                 painter.drawText(fill_rect, Qt.AlignCenter, f"{int(self._value)}%")

        # Draw Title at the bottom
        painter.setPen(Qt.white) # Black title text
        font = QFont('Arial', 12, QFont.Bold) # Regular weight font for title
        painter.setFont(font)
        # Position title rect below the main bar rect
        title_rect = QRectF(rect.left(), rect.bottom() + 3, rect.width(), 15)
        painter.drawText(title_rect, Qt.AlignCenter, self.title)
