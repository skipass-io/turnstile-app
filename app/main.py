import numpy as np
from PySide2 import QtCore
from PySide2.QtWidgets import (QApplication, QCheckBox, QHBoxLayout, QLabel,
                             QPushButton, QVBoxLayout, QWidget)

from picamera2 import Picamera2
from qgl_picam2_widget import QGlPicamera2


def request_callback(request):
    label.setText(''.join(f"{k}: {v}\n" for k, v in request.get_metadata().items()))


def cleanup():
    picam2.post_callback = None


picam2 = Picamera2()
picam2.post_callback = request_callback
picam2.configure(picam2.create_preview_configuration(main={"size": (800, 600)}))
app = QApplication([])


def on_button_clicked():
    button.setEnabled(False)
    cfg = picam2.create_still_configuration()
    picam2.switch_mode_and_capture_file(cfg, "test.jpg", signal_function=qpicamera2.signal_done)


def capture_done(job):
    picam2.wait(job)
    button.setEnabled(True)


overlay = np.zeros((300, 400, 4), dtype=np.uint8)
overlay[:150, 200:] = (255, 0, 0, 64)
overlay[150:, :200] = (0, 255, 0, 64)
overlay[150:, 200:] = (0, 0, 255, 64)


def on_checkbox_toggled(checked):
    if checked:
        qpicamera2.set_overlay(overlay)
    else:
        qpicamera2.set_overlay(None)


qpicamera2 = QGlPicamera2(picam2, width=800, height=600)
qpicamera2.done_signal.connect(capture_done)

button = QPushButton("Click to capture JPEG")
button.clicked.connect(on_button_clicked)
label = QLabel()
checkbox = QCheckBox("Set Overlay", checked=False)
checkbox.toggled.connect(on_checkbox_toggled)
window = QWidget()
window.setWindowTitle("Qt Picamera2 App")

label.setFixedWidth(400)
label.setAlignment(QtCore.Qt.AlignTop)
layout_h = QHBoxLayout()
layout_v = QVBoxLayout()
layout_v.addWidget(label)
layout_v.addWidget(checkbox)
layout_v.addWidget(button)
layout_h.addWidget(qpicamera2, 80)
layout_h.addLayout(layout_v, 20)
window.resize(1200, 600)
window.setLayout(layout_h)

picam2.start()
window.show()
app.exec_()
picam2.stop()