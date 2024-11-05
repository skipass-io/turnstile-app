import time
from io import BytesIO

from PySide2 import QtCore
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QLabel, QVBoxLayout, QWidget
import qrcode


class LeftWidget(QWidget):
    def __init__(self, qpicam2, font):
        """
        # Left widget on QGlPicamera2
        Show: Current time & QR Code

        @param qpicam2: QGlPicamera2
        @param font: QFont - `Poppins`
        """
        super().__init__(qpicam2)
        self.qrcode_text = None

        self._init_UI(font)

    def _init_UI(self, font):
        # Main colors
        color = "1197E4" 
        bg_color = "FFFFFF"

        # Set Layout
        self.setStyleSheet(f"background-color: #{bg_color};")
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create label for time
        self.label_time = QLabel("", self)
        self.label_time.setAlignment(QtCore.Qt.AlignCenter)
        self.label_time.setFixedSize(200, 65)
        self.label_time.setFont(font)
        self.label_time.setStyleSheet(f"color: #{color};")
        layout.addWidget(self.label_time)

        # Create label for QRCode
        self.label_qr = QLabel("", self)
        self.label_qr.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.label_qr)

        # Set layout for widget
        self.setLayout(layout)
        self.move(10, 10)
        self.setFixedSize(200, 250)

    def set_time(self):
        current_time = time.localtime()
        hours = current_time.tm_hour
        minutes = current_time.tm_min
        colon = ":" if current_time.tm_sec % 2 else " "
        self.label_time.setText(f"{hours}{colon}{minutes:02d}")

    def set_qrcode(self, text):
        """
        set qrcode image on `self.label_qr` QLabel

        @param text: text for the QRcode
        """
        if self.qrcode_text == text:
            return

        buf = BytesIO()
        img = qrcode.make(text)
        img.save(buf, "PNG")
        self.label_qr.setText("")
        qt_pixmap = QPixmap()
        qt_pixmap.loadFromData(buf.getvalue(), "PNG")
        qt_pixmap = qt_pixmap.scaled(212, 212, QtCore.Qt.KeepAspectRatio)
        self.label_qr.setPixmap(qt_pixmap)
