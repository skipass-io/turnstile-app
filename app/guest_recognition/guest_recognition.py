import os
import pickle
import time

import cv2 as cv
import numpy as np
from sklearn.preprocessing import LabelEncoder

from core.config import GuestRecognitionSettings
from .detectors import DetectorPyzbar, DetectorHaarcascade
from .embedder import Embedder
from .exceptions import NotCorrectFrameSizeGR
from .status_fsm import StatusFSM
from .turnstile_gpio import TurnstileGPIO
from .helpers import get_qrcode_label
from . import open_cv


_set = GuestRecognitionSettings()


class GuestRecognition:
    """That's how we let the guests through"""

    def _turnstile_performance(self):
        while self.TURNSTILE_PERFORMANCE is None:
            self.TURNSTILE_PERFORMANCE = os.environ.get("TURNSTILE_PERFORMANCE")
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

        self.performance_params = {}
        self.performance_params["fps"] = self._fps_performance()
        self.performance_params["wifi"] = True
        if self.TURNSTILE_PERFORMANCE == "True":
            open_cv.output_performance(
                frame=self.frame,
                params=self.performance_params,
                width=self.width,
                height=self.height,
            )

    def _fps_performance(self):
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

        self.cv_rgb = cv.cvtColor(self.frame, cv.COLOR_BGR2RGB)
        self.cv_gray = cv.cvtColor(self.frame, cv.COLOR_BGR2GRAY)

    def _find_qrcode(self):
        if self.status == StatusFSM.ALLOWED:
            return
        qr_code = self.detector_pyzbar.detect_qrcode(self.cv_gray)
        if not qr_code:
            return
        self.labels.append(qr_code)
        self.status = StatusFSM.QRCODE_SCANNING

    def _find_faces(self):
        if self.status == StatusFSM.ALLOWED:
            return

        detected_face = self.detector_haarcascade.detect_face(self.cv_gray)

        if (not detected_face) and (self.status != StatusFSM.QRCODE_SCANNING):
            self.status = StatusFSM.SEARCHING
            return

        # TODO: refactoring
        open_cv.output_face(
            self.frame,
            detected_face,
            self.AREA_START_RECOGNITION,
            self.AREA_STEP_BACK,
            self.TURNSTILE_PERFORMANCE,
        )
        x, y, w, h = detected_face
        facearea = int(w * h / 1000)
        if (facearea > self.AREA_START_RECOGNITION) & (facearea < self.AREA_STEP_BACK):
            self._face_recognition(face_coords=detected_face)
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
        ypred = self.embedder.get_embeddings(face_coords, self.cv_rgb)
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
        self._turnstile_performance()
        return self._processing()

    def __init__(self, frame_size):
        if (not frame_size) or (len(frame_size) != 2):
            raise NotCorrectFrameSizeGR(frame_size=frame_size)

        # Detectors
        self.detector_pyzbar = DetectorPyzbar()
        self.detector_haarcascade = DetectorHaarcascade(
            haarcascade_file=_set.data.haarcascade_path,
            scale_factor=_set.fd.scale_factor,
            min_neighbors=_set.fd.min_neighbors,
            scalar_detect=_set.fd.scalar_detect,
        )

        # Embedder
        self.embedder = Embedder()

        self.TURNSTILE_PERFORMANCE = None
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

        self.label_encoder = LabelEncoder()
        self.svm_model = None
        self.faces_embeddings = None

        self._load_data_for_ml()
