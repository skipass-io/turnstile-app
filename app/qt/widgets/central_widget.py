import time
from PySide2 import QtCore
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QProgressBar, QLabel, QVBoxLayout, QWidget


class CentralWidget(QWidget):
    def __init__(self, qpicam2, font, width, height):
        """
        # Central widget on QGlPicamera2
        Show: Current time & QR Code

        @param qpicam2: QGlPicamera2
        @param font: QFont - `Poppins`
        @param width: int - width of screen
        @param height: int - height of screen
        """
        super().__init__(qpicam2)

        self.width = width
        self.height = height
        self.font = font
        self.widget_width = 500
        self.widget_height = 125

        self.status_style = {
            "GET_CLOSER": {
                "color": "FFFFFF",
                "sec_color": "ADDBF6",
                "bg_color": "1197E4",
            },
            "STEP_BACK": {
                "color": "1197E4",
                "sec_color": "ADDBF6",
                "bg_color": "FFFFFF",
            },
            "QRCODE_SCANNING": {
                "color": "FFFFFF",
                "sec_color": "63008D",
                "bg_color": "C233FF",
            },
            "FACE_RECOGNITION": {
                "color": "FFFFFF",
                "sec_color": "63008D",
                "bg_color": "C233FF",
            },
            "ALLOWED": {
                "color": "FFFFFF",
                "sec_color": "004C20",
                "bg_color": "22CD69",
            },
            "NOT_ALLOWED": {
                "color": "ED451F",
                "sec_color": "000000",
                "bg_color": "FFFFFF",
            },
        }

        self._init_UI()

    def _init_UI(self):
        # Set Layout
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create label for time
        self.label_central = QLabel("Central Label", self)
        self.label_central.setAlignment(QtCore.Qt.AlignCenter)
        self.label_central.setFont(self.font)
        layout.addWidget(self.label_central)

        self.progress = QProgressBar(self)
        self.progress.setFont(self.font)

        self.progress.setValue(0)
        layout.addWidget(self.progress)


        # Set layout for widget
        self._set_style_sheets()
        self.setLayout(layout)
        self.move((self.width / 2) - int(self.widget_width / 2), self.height - (int(self.height / 4) + int(self.widget_height / 2)))
        self.setFixedSize(self.widget_width, self.widget_height)


    def _set_style_sheets(self, status=None):
        style = self.status_style.get(status)

        if not style:
            style = {
                "color": "000000",
                "sec_color": "808080",
                "bg_color": "FFFFFF",
            }

        self.setStyleSheet(f"background-color: #{style['bg_color']};")
        self.label_central.setStyleSheet(f"color: #{style['color']};")

        self.progress.setStyleSheet(
            f"""
            QProgressBar{{
                border: 4px solid #{style['bg_color']};
                text-align: center;
                font-size: 28px;
                color: #{style['sec_color']};
            }}

            QProgressBar::chunk {{
                
                background-color: #{style['color']};
            }}
            """
        )

        self.progress.setTextVisible(
            False if status == "NOT_ALLOWED" or status == "DETECTING" else True
        )

    def set_state(self, state):
        status = state.get("status")

        self._set_style_sheets(status)
        self.label_central.setText(state.get("label"))
        self.progress.setValue(state.get("progress"))
