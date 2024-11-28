import sys

from PySide2.QtGui import QFontDatabase, QFont
from PySide2.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QWidget,
)
from picamera2 import Picamera2, MappedArray

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
    with MappedArray(request, "main") as mapped_array:
        output = guest_recognition.run(mapped_array)
        left_widget.set_time()
        left_widget.set_qrcode("https://skipass.io") # TODO: With websockets
        right_widget.set_weather("", "-13")  # # TODO: With websockets
        right_widget.set_elevator("8", "8")  # # TODO: With websockets
        right_widget.set_slope("10", "16")  # # TODO: With websockets
        central_widget.set_state(output)


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

left_widget = LeftWidget(qpicam2=qpicamera2, font=font)
right_widget = RightWidget(qpicam2=qpicamera2, font=font, width=PICAM2_WIDTH)
central_widget = CentralWidget(
    qpicam2=qpicamera2, font=font, width=PICAM2_WIDTH, height=PICAM2_HEIGHT
)


window = QWidget()
window.setWindowTitle("turnstile-app")


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
