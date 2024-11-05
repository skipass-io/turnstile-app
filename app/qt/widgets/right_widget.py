from PySide2 import QtSvg, QtCore
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QWidget

from core.config import BASE_DIR


class RightWidget(QWidget):
    def __init__(self, qpicam2, font, width):
        """
        # Left widget on QGlPicamera2
        Show: Current weather, open lifts & slopes

        @param qpicam2: QGlPicamera2
        @param font: QFont - `Poppins`
        @param width: int - width of screen
        """
        super().__init__(qpicam2)

        self._init_UI(font, width)

    def _init_UI(self, font, width):
        # Main colors
        color = "1197E4"
        bg_color = "FFFFFF"

        # Set Layouts
        widget_width = 192
        widget_height = 65
        widget_size = (widget_width, widget_height)
        self.setStyleSheet(f"background-color: #{bg_color};")

        ## Vertical layout
        layout_v = QVBoxLayout()
        layout_v.setSpacing(0)
        layout_v.setContentsMargins(0, 0, 0, 0)

        ## Horizontal layout
        layout_h = QHBoxLayout()
        layout_h.setSpacing(0)
        layout_h.setContentsMargins(0, 0, 0, 0)

        lable_blank = QLabel()
        lable_blank.setFixedSize(widget_width, 10)
        layout_v.addWidget(lable_blank)

        # Create widget for weather
        self.widget_weather = WeatherWidget(font)
        # self.widget_weather.setFixedSize(*widget_size)
        layout_v.addWidget(self.widget_weather)

        lable_blank = QLabel()
        lable_blank.setFixedSize(widget_width, 10)
        layout_v.addWidget(lable_blank)

        # Create widget for elevator
        self.widget_elevator = ElevetorWidget(font)
        # self.widget_elevator.setFixedSize(*widget_size)
        layout_v.addWidget(self.widget_elevator)

        lable_blank = QLabel()
        lable_blank.setFixedSize(widget_width, 10)
        layout_v.addWidget(lable_blank)

        # Create widget for elevator
        self.widget_slope = SlopeWidget(font)
        # self.widget_slope.setFixedSize(*widget_size)
        layout_v.addWidget(self.widget_slope)

        lable_blank = QLabel()
        lable_blank.setFixedSize(widget_width, 10)
        layout_v.addWidget(lable_blank)

        # Create label blank
        self.label_blank = QLabel()
        self.label_blank.setFixedSize(8, 250)
        layout_h.addWidget(self.label_blank)
        layout_h.addLayout(layout_v)

        # Set layouts for widget
        self.setLayout(layout_h)
        self.setFixedSize(widget_width + 8, (widget_height * 3) + 40)
        self.move((width - 235), 10)

    def set_weather(self, type_weather, temperature):
        self.widget_weather.set_weater(
            type_weather=type_weather,
            temperature=temperature,
        )

    def set_elevator(self, active, total):
        self.widget_elevator.set_elevetor(
            active=active,
            total=total,
        )

    def set_slope(self, active, total):
        self.widget_slope.set_slope(
            active=active,
            total=total,
        )


class WeatherWidget(QWidget):
    def __init__(self, font):
        """
        # Weather widget for RightWidget
        Show: Current weather: icon & temperature

        @param font: QFont - `Poppins`
        """
        super().__init__()

        self._init_UI(font)

    def _init_UI(self, font):
        # Main colors
        color = "1197E4"
        bg_color = "FFFFFF"
        self.setStyleSheet(f"background-color: #{bg_color};")

        sunny_icon_path = f"{BASE_DIR}/app/assets/icons/sunny.svg"

        # Set Layouts
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.svg_icon = QtSvg.QSvgWidget(sunny_icon_path)
        self.svg_icon.setFixedSize(65, 65)
        self.svg_icon.setGeometry(50, 50, 759, 668)
        layout.addWidget(self.svg_icon)

        # Create label for temperature
        self.celsius_symbol = "°C"
        self.label_temperature = QLabel(f"{self.celsius_symbol}", self)
        self.label_temperature.setAlignment(QtCore.Qt.AlignCenter)
        self.label_temperature.setFont(font)
        self.label_temperature.setStyleSheet(f"color: #{color};")
        layout.addWidget(self.label_temperature)

        # Set layouts for widget
        self.setLayout(layout)

    def set_weater(self, type_weather, temperature):
        self.label_temperature.setText(f"{temperature}{self.celsius_symbol}")


class ElevetorWidget(QWidget):
    def __init__(self, font):
        """
        # Elevator widget for RightWidget
        Show: Current open and total elevators

        @param font: QFont - `Poppins`
        """
        super().__init__()

        self._init_UI(font)

    def _init_UI(self, font):
        # Main colors
        color = "1197E4"
        bg_color = "FFFFFF"
        self.setStyleSheet(f"background-color: #{bg_color};")

        gondola_lift_icon_path = f"{BASE_DIR}/app/assets/icons/gondola_lift.svg"

        # Set Layouts
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.svg_icon = QtSvg.QSvgWidget(gondola_lift_icon_path)
        self.svg_icon.setFixedSize(65, 65)
        self.svg_icon.setGeometry(50, 50, 759, 668)
        layout.addWidget(self.svg_icon)

        # Create label for elevator
        self.label_elevetor = QLabel(f"", self)
        self.label_elevetor.setAlignment(QtCore.Qt.AlignCenter)
        self.label_elevetor.setFont(font)
        self.label_elevetor.setStyleSheet(f"color: #{color};")
        layout.addWidget(self.label_elevetor)

        # Set layouts for widget
        self.setLayout(layout)

    def set_elevetor(self, active, total):
        self.label_elevetor.setText(f"{active}/{total}")


class SlopeWidget(QWidget):
    def __init__(self, font):
        """
        # Slope widget for RightWidget
        Show: Current open and slopes

        @param font: QFont - `Poppins`
        """
        super().__init__()

        self._init_UI(font)

    def _init_UI(self, font):
        # Main colors
        color = "1197E4" 
        bg_color = "FFFFFF"
        self.setStyleSheet(f"background-color: #{bg_color};")

        downhill_skiing_icon_path = f"{BASE_DIR}/app/assets/icons/downhill_skiing.svg"

        # Set Layouts
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.svg_icon = QtSvg.QSvgWidget(downhill_skiing_icon_path)
        self.svg_icon.setFixedSize(65, 65)
        self.svg_icon.setGeometry(50, 50, 759, 668)
        layout.addWidget(self.svg_icon)

        # Create label for slope
        self.label_slope = QLabel(f"", self)
        self.label_slope.setAlignment(QtCore.Qt.AlignCenter)
        self.label_slope.setFont(font)
        self.label_slope.setStyleSheet(f"color: #{color};")
        layout.addWidget(self.label_slope)

        # Set layouts for widget
        self.setLayout(layout)

    def set_slope(self, active, total):
        self.label_slope.setText(f"{active}/{total}")
