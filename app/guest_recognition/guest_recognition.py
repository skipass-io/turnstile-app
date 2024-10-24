import pickle
import functools
import time

import cv2 as cv
import numpy as np
from keras_facenet import FaceNet
from sklearn.preprocessing import LabelEncoder
from pyzbar.pyzbar import decode as pyzbar_decoder
from pyzbar.pyzbar import Decoded as PyzbarDecoded

from core.config import GuestRecognitionSettings
from .exceptions import NotCorrectStatusGR, NotCorrectFrameSizeGR
from .status_fsm import StatusFSM
from .turnstile_gpio import TurnstileGPIO


_settings = GuestRecognitionSettings()


class GuestRecognition:
    """That's how we let the guests through"""

    def _check_correct_status(self, correct_statuses):
        if self.status not in correct_statuses:
            raise NotCorrectStatusGR(
                current_status=self.status,
                correct_statuses=correct_statuses,
            )

    def _load_data_for_ml(self):
        self.svm_model = pickle.load(open(_settings.data.svm_model_path, "rb"))
        self.faces_embeddings = np.load(_settings.data.embeddings_path)
        Y = self.faces_embeddings["arr_1"]
        self.label_encoder.fit(Y)
        self.status = StatusFSM.SEARCHING

    def _cv_img(self, color):
        match color:
            case "rgb":
                cv_color = cv.COLOR_BGR2RGB
            case "gray":
                cv_color = cv.COLOR_BGR2GRAY
            case _:
                raise Exception("Need color for get_cv_img: gray or rgb")
        return cv.cvtColor(self.frame, cv_color)

    def _set_frame(self, mapped_array):
        # self._check_correct_status(correct_statuses=[StatusFSM.SEARCHING, ])

        self.frame = mapped_array.array
        self.cv_rgb = self._cv_img("rgb")
        self.cv_gray = self._cv_img("gray")

    def _find_qrcode(self):
        if self.status == StatusFSM.ALLOWED:
            return
        # self._check_correct_status(correct_statuses=[StatusFSM.GET_READY])
        qr_codes = [qr for qr in self.qr_decoder(self.cv_gray) if qr.type == "QRCODE"]
        if len(qr_codes) == 0:
            return
        elif len(qr_codes) == 1:
            qr_code = qr_codes[0]
        else:
            qr_code = functools.reduce(
                lambda qr_a, qr_b: (
                    qr_a
                    if (qr_a.rect[2] + qr_a.rect[3]) > (qr_b.rect[2] + qr_b.rect[3])
                    else qr_b
                ),
                qr_codes,
            )
        if (self.status == StatusFSM.FACE_RECOGNITION) or (
            self.status == StatusFSM.GET_CLOSER
        ):
            self._reset_guest_recognition()
        label = qr_code.data.decode("utf-8")
        self.labels.append(label)
        self.status = StatusFSM.QRCODE_SCANNING

    def _find_faces(self):
        if self.status == StatusFSM.ALLOWED:
            return
        # self._check_correct_status(correct_statuses=[StatusFSM.GET_READY])
        fd_settings = _settings.face_detector_settings

        found_faces = self.face_detector.detectMultiScale(
            image=self.cv_gray,
            scaleFactor=fd_settings.scale_factor,
            minNeighbors=fd_settings.min_neighbors,
            minSize=(
                int(self.width / fd_settings.scalar_detect),
                int(self.height / fd_settings.scalar_detect),
            ),
        )
        if (len(found_faces) == 0) and (self.status != StatusFSM.QRCODE_SCANNING):
            self.status = StatusFSM.SEARCHING
            return

        for face in found_faces:
            x, y, w, h = face
            if (w > (self.width / fd_settings.scalar_recognition)) & (
                h > (self.height / fd_settings.scalar_recognition)
            ):
                self._face_recognition(face_coords=face)
                self.status = StatusFSM.FACE_RECOGNITION
            else:
                self.status = StatusFSM.GET_CLOSER

    def _face_recognition(self, face_coords):
        x, y, w, h = face_coords
        face_img = self.cv_rgb[y : y + h, x : x + w]
        face_img = cv.resize(face_img, (160, 160))
        face_img = np.expand_dims(face_img, axis=0)
        ypred = self.facenet.embeddings(face_img)
        face_name = self.svm_model.predict(ypred)
        label = self.label_encoder.inverse_transform(face_name)[0]
        self.labels.append(label)

    def _most_frequent_label(self):
        if len(self.labels) >= 15:  # TODO: instead "15" - in settings or smth params
            frequent_label = max(set(self.labels), key=self.labels.count)
            self.guest_label = (
                frequent_label if self.labels.count(frequent_label) >= 13 else None
            )  # TODO: instead "13" - in settings or smth params

            if self.guest_label:
                self.status = StatusFSM.ALLOWED  # TODO: ask DB for allowed or not

    def _checking_time_allowed(self):
        if not self.start_time_allowed:
            self.start_time_allowed = time.time()
            self.turnstile_gpio.open_gate()
            return

        checking_time = time.time() - self.start_time_allowed
        if (
            checking_time >= 4
        ):  # TODO: instead `10` second - diffrent value from `_settings`
            self._reset_guest_recognition()
            self.turnstile_gpio.close_gate()

    def _get_current_time(self):
        """retrun str - `HH:MM`"""
        current_time = time.localtime()
        hours = current_time.tm_hour
        minutes = current_time.tm_min
        return f"{hours}:{minutes:02d}"

    def _reset_guest_recognition(self):  # TODO: Rename
        self.status = StatusFSM.SEARCHING
        self.labels = []
        self.guest_label = None
        self.start_time_allowed = None

    def _processing(self):
        match self.status:
            case StatusFSM.SEARCHING:
                status_hex = _settings.colors.LIGHT_BLUE_HEX
            case StatusFSM.GET_CLOSER:
                status_hex = _settings.colors.BLUE_HEX
            case StatusFSM.QRCODE_SCANNING:
                self._most_frequent_label()
                status_hex = _settings.colors.MAGENTA_HEX
            case StatusFSM.FACE_RECOGNITION:
                self._most_frequent_label()
                status_hex = _settings.colors.MAGENTA_HEX
            case StatusFSM.ALLOWED:
                self._checking_time_allowed()
                status_hex = _settings.colors.GREEN_HEX
            # case StatusFSM.NOT_ALLOWED:
            #     status_hex = _settings.colors.RED_HEX
            # case StatusFSM.ERROR:
            #     status_hex = _settings.colors.RED_HEX

        text_top = self.status.value.upper()
        text_bottom = (
            f"Welcome {self.guest_label}!"
            if self.guest_label
            else self._get_current_time()  # TODO: Change it on something (may be weather from fnugg)
        )

        return text_top, text_bottom, status_hex

    def run(self, mapped_array):
        """Processing PiCamera frame"""
        self._set_frame(mapped_array)
        self._find_qrcode()
        self._find_faces()
        text_top, text_bottom, status_hex = self._processing()
        return text_top, text_bottom, status_hex

    def __init__(self, frame_size):
        if (not frame_size) or (len(frame_size) != 2):
            raise NotCorrectFrameSizeGR(frame_size=frame_size)

        self.status = None
        self.guest_label = None
        self.start_time_allowed = None
        self.labels = []
        self.turnstile_gpio = TurnstileGPIO()
        self.frame = None
        self.width = frame_size[0]
        self.height = frame_size[1]
        self.cv_rgb = None
        self.cv_gray = None
        self.face_detector = cv.CascadeClassifier(_settings.data.haarcascade_path)
        self.qr_decoder = pyzbar_decoder
        self.label_encoder = LabelEncoder()
        self.facenet = FaceNet()
        self.svm_model = None
        self.faces_embeddings = None

        self._load_data_for_ml()
