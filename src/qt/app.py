import sys

from PySide2.QtGui import QFontDatabase, QFont
from PySide2.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QWidget,
)
from picamera2 import Picamera2, MappedArray
from libcamera import controls

from core import settings
from guest_recognition import GuestRecognition
from qt.picamera_controls import PicameraContols
from qt.widgets import QGlPicamera2, LeftWidget, CentralWidget
from qt.helpers import get_screen_params


app = QApplication(sys.argv)
PICAM2_WIDTH, PICAM2_HEIGHT = get_screen_params(app)

gr = GuestRecognition(
    frame_size=(PICAM2_WIDTH, PICAM2_HEIGHT),
)

picam_controls = PicameraContols()

def request_callback(request):
    with MappedArray(request, "main") as mapped_array:
        gr.run(mapped_array)
        left_widget.set_time()
        left_widget.set_qrcode(settings.app.recruitment_form_url)
        central_widget.set_state(
            status=gr.status,
            progress=gr.progress,
        )
        if controls := picam_controls.is_new_settings(
            turnstile_settings=gr.turnstile_settings
        ):
            picam2.set_controls(controls)


def cleanup():
    picam2.post_callback = None


picam2 = Picamera2()
picam2.post_callback = request_callback
picam2.configure(
    picam2.create_preview_configuration(
        main={"size": (PICAM2_WIDTH, PICAM2_HEIGHT)},
    )
)
picam2.set_controls({"AwbMode":"Daylight"})

# Add Popins font
font_id = QFontDatabase.addApplicationFont(str(settings.qt.font_path))
font_name = QFontDatabase.applicationFontFamilies(font_id)[0]
font = QFont(font_name, 30)


qpicamera2 = QGlPicamera2(
    picam2,
    width=PICAM2_WIDTH,
    height=PICAM2_HEIGHT,
    bg_colour=(255, 255, 255),
    keep_ar=False,
)

left_widget = LeftWidget(
    qpicam2=qpicamera2,
    font=font,
)
central_widget = CentralWidget(
    qpicam2=qpicamera2,
    font=font,
    width=PICAM2_WIDTH,
    height=PICAM2_HEIGHT,
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
