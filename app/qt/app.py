import sys

from PySide2.QtGui import QFontDatabase, QFont
from PySide2.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QWidget,
)
from picamera2 import Picamera2, MappedArray
from libcamera import controls

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
        # exposure_time = 9000  # 16 миллисекунд (эксперимент)
        # gain = 1.0  # Минимальное усиление
        # picam2.set_controls({"ExposureTime": exposure_time, "AnalogueGain": gain})
        
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

# rpi-camera-settings
picam2.set_controls({"AeEnable": True})
#picam2.set_controls({"ExposureValue": 5.0})
#picam2.set_controls({"AeConstraintMode": controls.AeConstraintModeEnum.Highlight})
picam2.set_controls({"AeMeteringMode": controls.AeMeteringModeEnum.Spot})
#picam2.set_controls({"AeExposureMode": controls.AeExposureModeEnum.Normal})

# Устанавливаем фиксированную экспозицию и усиление
    # Значения нужно будет подобрать экспериментально
    # Экспозиция в микросекундах (меньше значение - темнее изображение)
    # exposure_time = 10000  # 10 миллисекунд (для яркого освещения попробуйте меньшие значения)
# exposure_time = 10000  # 16 миллисекунд (эксперимент)
# exposure_time = 20000  # 20 миллисекунд (для среднего освещения)
    # exposure_time = 33000  # 33 миллисекунды (для более темных условий)
    
    # Аналоговое усиление (gain)
# gain = 1.0  # Минимальное усиление
# gain = 2.0  # Среднее усиление
    # gain = 4.0  # Высокое усиление (может добавить шум)

# picam2.set_controls({"ExposureTime": exposure_time, "AnalogueGain": gain})

###
picam2.set_controls({"AwbMode": controls.AwbModeEnum.Daylight})
# picam2.set_controls({"AeMeteringMode": controls.AeMeteringModeEnum.Spot})


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
