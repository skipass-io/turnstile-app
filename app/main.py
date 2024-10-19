import sys

from PySide2 import QtCore
from PySide2.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)
from picamera2 import Picamera2, MappedArray

from guest_recognition import GuestRecognition, QGlPicamera2

# TODO: target for vetical screen size 720:1280
PICAM2_WIDTH = 720
PICAM2_HEIGHT = 1280


guest_recognition = GuestRecognition(frame_size=(PICAM2_WIDTH, PICAM2_HEIGHT))

status_text = None
status_hex = None


def request_callback(request):
    with MappedArray(request, "main") as m:
        status_text, label_text, status_hex = guest_recognition.run(mapped_array=m)
    label_top.setText("Status:", status_text)
    label_bottom.setText("Label:", label_text)
    window.setStyleSheet(f"background-color: #{status_hex};")


def cleanup():
    picam2.post_callback = None


picam2 = Picamera2()
picam2.post_callback = request_callback
picam2.configure(
    picam2.create_preview_configuration(main={"size": (PICAM2_WIDTH, PICAM2_HEIGHT)})
)
app = QApplication(sys.argv)


qpicamera2 = QGlPicamera2(
    picam2,
    width=PICAM2_WIDTH,
    height=PICAM2_HEIGHT,
    bg_colour=(255, 255, 255),
    keep_ar=False,
)
label_top = QLabel()
label_bottom = QLabel()
window = QWidget()
window.setWindowTitle("turnstile-app")
window.setAttribute(QtCore.Qt.WA_StyledBackground, True)


label_top.setFixedHeight(50)
label_bottom.setFixedHeight(50)
label_top.setAlignment(QtCore.Qt.AlignTop)
label_bottom.setAlignment(QtCore.Qt.AlignTop)


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
