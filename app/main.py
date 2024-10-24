import sys

from PySide2 import QtCore
from PySide2.QtGui import QFontDatabase, QFont
from PySide2.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)
from picamera2 import Picamera2, MappedArray

from core.config import AppSettings
from guest_recognition import GuestRecognition, QGlPicamera2


app_settings = AppSettings()


PICAM2_WIDTH, PICAM2_HEIGHT = app_settings.picam2_horizontal_size

guest_recognition = GuestRecognition(frame_size=(PICAM2_WIDTH, PICAM2_HEIGHT))


def request_callback(request):
    with MappedArray(request, "main") as m:
        text_top, text_bottom, status_hex = guest_recognition.run(
            mapped_array=m
        )
    label_top.setText(text_top)
    label_bottom.setText(text_bottom)
    window.setStyleSheet(f"background-color: #{status_hex};")


def cleanup():
    picam2.post_callback = None


picam2 = Picamera2()
picam2.post_callback = request_callback
picam2.configure(
    picam2.create_preview_configuration(main={"size": (PICAM2_WIDTH, PICAM2_HEIGHT)})
)
app = QApplication(sys.argv)
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
label_top = QLabel()
label_bottom = QLabel()
label_top.setFont(font)
label_bottom.setFont(font)
label_top.setStyleSheet("color: #fff;")
label_bottom.setStyleSheet("color: #fff;")
window = QWidget()
window.setWindowTitle("turnstile-app")
window.setAttribute(QtCore.Qt.WA_StyledBackground, True)


label_top.setFixedHeight(50)
label_bottom.setFixedHeight(50)
label_top.setAlignment(QtCore.Qt.AlignCenter)
label_bottom.setAlignment(QtCore.Qt.AlignCenter)


layout_v = QVBoxLayout()
layout_v.addWidget(label_top)
layout_v.addWidget(qpicamera2)
layout_v.addWidget(label_bottom)
window.setLayout(layout_v)
window.showFullScreen()


# screen info
screen = app.primaryScreen()
print("Screen: %s" % screen.name())
size = screen.size()
print("Size: %d x %d" % (size.width(), size.height()))
rect = screen.availableGeometry()
print("Available: %d x %d" % (rect.width(), rect.height()))


def main():
    picam2.start()
    window.show()
    app.exec_()
    picam2.stop()


if __name__ == "__main__":
    main()
