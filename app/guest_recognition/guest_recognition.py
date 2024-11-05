import os
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
from .exceptions import NotCorrectFrameSizeGR
from .status_fsm import StatusFSM
from .turnstile_gpio import TurnstileGPIO
from .helpers import get_qrcode_label
from . import open_cv


_set = GuestRecognitionSettings()


class GuestRecognition:
    """That's how we let the guests through"""

    def _turnstile_perfomance(self):
        while self.TURNSTILE_PERFOMANCE is None:
            self.TURNSTILE_PERFOMANCE = os.environ.get("TURNSTILE_PERFOMANCE")
        while self.AREA_START_RECOGNITION is None:
            self.AREA_START_RECOGNITION = os.environ.get("AREA_START_RECOGNITION")
            if self.AREA_START_RECOGNITION:
                self.AREA_START_RECOGNITION = int(self.AREA_START_RECOGNITION)
        while self.AREA_STEP_BACK is None:
            self.AREA_STEP_BACK = os.environ.get("AREA_STEP_BACK")
            if self.AREA_STEP_BACK:
                self.AREA_STEP_BACK = int(self.AREA_STEP_BACK)
        while self.FACE_RECOGNITION_LABELS_COUNT is None:
            self.FACE_RECOGNITION_LABELS_COUNT = os.environ.get(
                "FACE_RECOGNITION_LABELS_COUNT"
            )
            if self.FACE_RECOGNITION_LABELS_COUNT:
                self.FACE_RECOGNITION_LABELS_COUNT = int(
                    self.FACE_RECOGNITION_LABELS_COUNT
                )
        while self.FACE_RECOGNITION_PERCENT is None:
            self.FACE_RECOGNITION_PERCENT = os.environ.get("FACE_RECOGNITION_PERCENT")
            if self.FACE_RECOGNITION_PERCENT:
                self.FACE_RECOGNITION_PERCENT = int(self.FACE_RECOGNITION_PERCENT)

        self.perfomance_params = {}
        self.perfomance_params["fps"] = self._fps_perfomance()
        self.perfomance_params["wifi"] = True
        if self.TURNSTILE_PERFOMANCE == "True":
            open_cv.output_perfomance(
                frame=self.frame,
                params=self.perfomance_params,
                width=self.width,
                height=self.height,
            )

    def _fps_perfomance(self):
        self.fps += 1
        elapsed_time = time.time() - self.start_time

        if elapsed_time >= 1.0:
            self.fps_calc = self.fps / elapsed_time
            self.fps = 0
            self.start_time = time.time()

        return f"{self.fps_calc:.2f}"

    def _load_data_for_ml(self):
        self.svm_model = pickle.load(open(_set.data.svm_model_path, "rb"))
        self.faces_embeddings = np.load(_set.data.embeddings_path)
        Y = self.faces_embeddings["arr_1"]
        self.label_encoder.fit(Y)
        self.status = StatusFSM.SEARCHING

    def _set_frame(self, mapped_array):
        self.frame = mapped_array.array

        # self.cv_rgb = cv.cvtColor(self.frame, cv.COLOR_YUV420p2RGB)
        # self.cv_gray = cv.cvtColor(self.frame, cv.COLOR_YUV420p2GRAY)
        self.cv_rgb = cv.cvtColor(self.frame, cv.COLOR_BGR2RGB)
        self.cv_gray = cv.cvtColor(self.frame, cv.COLOR_BGR2GRAY)

    def _find_qrcode(self):
        if self.status == StatusFSM.ALLOWED:
            return
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

    def _face_detection(self):
        found_faces = self.face_detector.detectMultiScale(
            image=self.cv_gray,
            scaleFactor=_set.fd.scale_factor,
            minNeighbors=_set.fd.min_neighbors,
            minSize=(
                int(self.width / _set.fd.scalar_detect),
                int(self.height / _set.fd.scalar_detect),
            ),
        )
        count_faces = len(found_faces)
        return found_faces, count_faces

    def _find_faces(self):
        if self.status == StatusFSM.ALLOWED:
            return

        found_faces, count_faces = self._face_detection()
        if (count_faces == 0) and (self.status != StatusFSM.QRCODE_SCANNING):
            self.status = StatusFSM.SEARCHING
            return

        for face in found_faces:
            open_cv.output_face(
                self.frame,
                face,
                self.AREA_START_RECOGNITION,
                self.AREA_STEP_BACK,
                self.TURNSTILE_PERFOMANCE,
            )
            x, y, w, h = face
            facearea = int(w * h / 1000)
            if (facearea > self.AREA_START_RECOGNITION) & (
                facearea < self.AREA_STEP_BACK
            ):
                self._face_recognition(face_coords=face)
                self.status = StatusFSM.FACE_RECOGNITION
            elif facearea > self.AREA_STEP_BACK:
                self._reset_guest_recognition()
                self.status = StatusFSM.STEP_BACK
                self.progerss_value = int(facearea / self.AREA_STEP_BACK * 100)

            else:
                self._reset_guest_recognition()
                self.status = StatusFSM.GET_CLOSER
                self.progerss_value = int(facearea / self.AREA_START_RECOGNITION * 100)

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
        frequent_labels_count = int(
            self.FACE_RECOGNITION_LABELS_COUNT * self.FACE_RECOGNITION_PERCENT / 100
        )
        if len(self.labels) >= self.FACE_RECOGNITION_LABELS_COUNT:
            frequent_label = max(set(self.labels), key=self.labels.count)
            self.guest_label = (
                frequent_label
                if self.labels.count(frequent_label) >= frequent_labels_count
                else None
            )

            if self.guest_label:
                self.status = StatusFSM.ALLOWED  # TODO: ask DB for allowed or not

        return int(len(self.labels) / self.FACE_RECOGNITION_LABELS_COUNT * 100)

    def _checking_time_allowed(self):
        if not self.start_time_allowed:
            self.start_time_allowed = time.time()
            self.turnstile_gpio.open_gate()
            return

        checking_time = time.time() - self.start_time_allowed
        if checking_time >= 4:  # TODO: instead `10` second - diffrent value from `_set`
            self._reset_guest_recognition()
            self.turnstile_gpio.close_gate()

    def _reset_guest_recognition(self):  # TODO: Rename
        self.status = StatusFSM.SEARCHING
        self.labels = []
        self.guest_label = None
        self.start_time_allowed = None

    def _set_state(self):
        # status, label, progress, pull
        state = {
            "status": self.status.name,
            "label": self.status.name,
            "progress": 55,
        }
        match self.status:
            case StatusFSM.SEARCHING:
                pass
            case StatusFSM.GET_CLOSER:
                state["progress"] = self.progerss_value
            case StatusFSM.STEP_BACK:
                state["progress"] = self.progerss_value
            case StatusFSM.QRCODE_SCANNING:
                pass
            case StatusFSM.FACE_RECOGNITION:
                state["progress"] = self._most_frequent_label()
                pass
            case StatusFSM.ALLOWED:
                state["label"] = self.guest_label
                state["progress"] = 100
                self._checking_time_allowed()
                pass
            case StatusFSM.NOT_ALLOWED:
                pass

        return state

    def _processing(self):
        """processing of all data in a loop with the received frame"""
        state = {}
        state["time"] = True  # Helpers
        state["qr"] = get_qrcode_label()  # DB / Helpers
        state["state"] = self._set_state()
        return state
        # labels['weather'] = get_weather() # DB / Helpers
        # labels['resort'] = get_resort() # DB / Helpers
        # labels['status'] =

        # match self.status:
        #     case StatusFSM.SEARCHING:
        #         status_hex = _set.colors.LIGHT_BLUE_HEX
        #     case StatusFSM.GET_CLOSER:
        #         status_hex = _set.colors.BLUE_HEX
        #     case StatusFSM.QRCODE_SCANNING:
        #         self._most_frequent_label()
        #         status_hex = _set.colors.MAGENTA_HEX
        #     case StatusFSM.FACE_RECOGNITION:
        #         self._most_frequent_label()
        #         status_hex = _set.colors.MAGENTA_HEX
        #     case StatusFSM.ALLOWED:
        #         self._checking_time_allowed()
        #         status_hex = _set.colors.GREEN_HEX
        #     # case StatusFSM.NOT_ALLOWED:
        #     #     status_hex = _set.colors.RED_HEX
        #     # case StatusFSM.ERROR:
        #     #     status_hex = _set.colors.RED_HEX

        # text_top = self.status.value.upper()
        # text_bottom = (
        #     f"Welcome {self.guest_label}!"
        #     if self.guest_label
        #     else self._get_current_time()  # TODO: Change it on something (may be weather from fnugg)
        # )

    def run(self, mapped_array):
        """Processing PiCamera frame"""
        self._set_frame(mapped_array)
        self._find_qrcode()
        self._find_faces()
        self._turnstile_perfomance()
        return self._processing()

    def __init__(self, frame_size):
        if (not frame_size) or (len(frame_size) != 2):
            raise NotCorrectFrameSizeGR(frame_size=frame_size)

        self.TURNSTILE_PERFOMANCE = None
        self.AREA_START_RECOGNITION = None
        self.AREA_STEP_BACK = None
        self.FACE_RECOGNITION_LABELS_COUNT = None
        self.FACE_RECOGNITION_PERCENT = None

        self.fps = 0
        self.fps_calc = "calculated"
        self.start_time = time.time()

        self.status = StatusFSM.SEARCHING
        self.guest_label = None
        self.start_time_allowed = None
        self.labels = []
        self.turnstile_gpio = TurnstileGPIO()
        self.frame = None
        self.width = frame_size[0]
        self.height = frame_size[1]
        self.cv_rgb = None
        self.cv_gray = None
        self.face_detector = cv.CascadeClassifier(_set.data.haarcascade_path)
        self.qr_decoder = pyzbar_decoder
        self.label_encoder = LabelEncoder()
        self.facenet = FaceNet()
        self.svm_model = None
        self.faces_embeddings = None

        self._load_data_for_ml()
