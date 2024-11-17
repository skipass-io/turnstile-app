import sys
from io import BytesIO

from PySide2 import QtCore
from PySide2.QtGui import QFontDatabase, QFont, QPixmap, QColor, QPainter, QBrush
from PySide2.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)
from picamera2 import Picamera2, MappedArray
import qrcode

from core.config import AppSettings
from guest_recognition import GuestRecognition
from .widgets import QGlPicamera2, LeftWidget, RightWidget, CentralWidget
from .helpers import get_screen_params


app = QApplication(sys.argv)
app_settings = AppSettings()


PICAM2_WIDTH, PICAM2_HEIGHT = get_screen_params(app)

guest_recognition = GuestRecognition(frame_size=(PICAM2_WIDTH, PICAM2_HEIGHT))

pull_up = False
pull_down = False


def request_callback(request):
    global pull_up, pull_down
    with MappedArray(request, "main") as m:
        state = guest_recognition.run(mapped_array=m)
        left_widget.set_time()
        left_widget.set_qrcode(state.get("qr"))
        right_widget.set_weather("", "-13")  # TODO
        right_widget.set_elevator("8", "8")  # TODO
        right_widget.set_slope("10", "16")  # TODO
        central_widget.set_state(state.get("state"))


def cleanup():
    picam2.post_callback = None


picam2 = Picamera2()
picam2.post_callback = request_callback
picam2.configure(
    picam2.create_preview_configuration(
        main={"size": (PICAM2_WIDTH, PICAM2_HEIGHT)},
    )
)


# Add Popins font
font_id = QFontDatabase.addApplicationFont(app_settings.font_path)
font_name = QFontDatabase.applicationFontFamilies(font_id)[0]
font = QFont(font_name, 30)


qpicamera2 = QGlPicamera2(
    picam2,
    width=PICAM2_WIDTH,
    height=PICAM2_HEIGHT,
    bg_colour=(255, 255, 255),
    keep_ar=False,
)

# Left side screen
left_widget = LeftWidget(qpicam2=qpicamera2, font=font)
right_widget = RightWidget(qpicam2=qpicamera2, font=font, width=PICAM2_WIDTH)
central_widget = CentralWidget(
    qpicam2=qpicamera2, font=font, width=PICAM2_WIDTH, height=PICAM2_HEIGHT
)
central_widget_pull = central_widget.pull


window = QWidget()
window.setWindowTitle("turnstile-app")
# window.setAttribute(QtCore.Qt.WA_StyledBackground, True)


layout_v = QVBoxLayout()
layout_v.addWidget(qpicamera2)
window.setLayout(layout_v)
window.setStyleSheet("background-color: #000;")
window.showFullScreen()


def exec():
    picam2.start()
    window.show()
    app.exec_()
    picam2.stop()
