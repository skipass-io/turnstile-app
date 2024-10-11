import numpy as np
from PySide2 import QtCore
from PySide2.QtWidgets import (
    QApplication,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from picamera2 import Picamera2
from qgl_picam2_widget import QGlPicamera2


def request_callback(request):
    label_top.setText("Top")
    label_bottom.setText("Bottom")
    window.setStyleSheet('background-color: green;')
    # label_top.setText("".join(f"{k}: {v}\n" for k, v in request.get_metadata().items()))


def cleanup():
    picam2.post_callback = None


picam2 = Picamera2()
picam2.post_callback = request_callback
PICAM2_WIDTH=1024
PICAM2_HEIGHT=768
picam2.configure(
    picam2.create_preview_configuration(main={"size": (PICAM2_WIDTH, PICAM2_HEIGHT)})
)
app = QApplication([])


qpicamera2 = QGlPicamera2(picam2, width=PICAM2_WIDTH, height=PICAM2_HEIGHT)
label_top = QLabel()
label_bottom = QLabel()
window = QWidget()
window.setWindowTitle("Qt Picamera2 App")
window.setAttribute(QtCore.Qt.WA_StyledBackground, True)


label_top.setFixedHeight(80)
label_top.setAlignment(QtCore.Qt.AlignTop)

label_bottom.setFixedHeight(40)

layout_v = QVBoxLayout()
layout_v.addWidget(label_top)
layout_v.addWidget(qpicamera2)
layout_v.addWidget(label_bottom)
# window.resize(1200, 600)
window.setLayout(layout_v)
window.showFullScreen()


def main():
    picam2.start()
    window.show()
    app.exec_()
    picam2.stop()


if __name__ == "__main__":
    main()
