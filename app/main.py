import sys
import numpy as np
from PySide2 import QtCore
from PySide2.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from picamera2 import Picamera2
from qgl_picam2_widget import QGlPicamera2


def request_callback(request):
    label_top.setText("Top")
    label_bottom.setText("Bottom")
    window.setStyleSheet("background-color: #000;")
    # label_top.setText("".join(f"{k}: {v}\n" for k, v in request.get_metadata().items()))


def cleanup():
    picam2.post_callback = None


picam2 = Picamera2()
picam2.post_callback = request_callback
PICAM2_WIDTH = 720 #720 #1366
PICAM2_HEIGHT = 768 #768
# 1366 x 768
picam2.configure(
    picam2.create_preview_configuration(main={"size": (PICAM2_WIDTH, PICAM2_HEIGHT)})
)
app = QApplication(sys.argv)


qpicamera2 = QGlPicamera2(
    picam2, width=PICAM2_WIDTH, height=PICAM2_HEIGHT, bg_colour=(255, 255, 255), keep_ar=False
)
label_top = QLabel()
label_bottom = QLabel()
window = QWidget()
window.setWindowTitle("Qt Picamera2 App")
window.setAttribute(QtCore.Qt.WA_StyledBackground, True)


label_top.setFixedWidth(323)
label_bottom.setFixedWidth(323)
label_top.setAlignment(QtCore.Qt.AlignTop)
label_bottom.setAlignment(QtCore.Qt.AlignTop)


layout_h = QHBoxLayout()
layout_h.addWidget(label_top)
layout_h.addWidget(qpicamera2)
layout_h.addWidget(label_bottom)
# window.resize(1200, 600)
window.setLayout(layout_h)
window.showFullScreen()

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
