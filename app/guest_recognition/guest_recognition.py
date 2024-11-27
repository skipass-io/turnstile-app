import pickle
import time

import cv2 as cv
import numpy as np
from sklearn.preprocessing import LabelEncoder

from core.config import GuestRecognitionSettings
from db import database
from .detectors import DetectorBlazeface, DetectorHaarcascade, DetectorPyzbar
from .embedder import Embedder
from .status_fsm import StatusFSM
from .turnstile_gpio import TurnstileGPIO
from .helpers import get_qrcode_label
from . import open_cv


_set = GuestRecognitionSettings()


class GuestRecognition:
    def __init__(self, frame_size):
        # Guest Recognition
        self.status = StatusFSM.DETECTING
        self.guest_recognition_iteration = 0
        self.collected_labels = []
        self.passage_label = None
        self.start_allowed_time = None
        self.processed_output = {}

        # Frame
        self.width = frame_size[0]
        self.height = frame_size[1]
        self.frame = None
        self.cv_rgb = None
        self.cv_gray = None

        # Face Detectors
        self.face_detector = None
        self.detector_blazeface = DetectorBlazeface(
            model_asset_path=_set.data.blazeface_path
        )
        self.detector_haarcascade = DetectorHaarcascade(
            haarcascade_file=_set.data.haarcascade_path,
            scale_factor=_set.fd.scale_factor,
            min_neighbors=_set.fd.min_neighbors,
            scalar_detect=_set.fd.scalar_detect,
        )

        # QR Code Detector
        self.detector_pyzbar = DetectorPyzbar()

        # Embedder
        self.embedder = Embedder()

        # SVM
        self.label_encoder = LabelEncoder()
        self.svm_model = None
        self.faces_embeddings = None
        self._load_ml_data()

        # GPIO
        self.turnstile_gpio = TurnstileGPIO()

        # FPS
        self.fps = 0
        self.fps_calc = "calculated"
        self.start_time = time.time()

        # Set Settings
        self._set_app_settings()

    def run(self, mapped_array):
        """
        Processing PiCamera frame for Detecting Face or QR Code
        """
        self._pre_processing_stage(mapped_array)
        self._processing_stage()
        self._post_processing_stage()

        return self.processed_output

    # PRE PROCESSING STAGE
    def _pre_processing_stage(self, mapped_array):
        self._pre_processing_frame(mapped_array)

    def _pre_processing_frame(self, mapped_array):
        # Main frame
        self.frame = mapped_array.array

        # Open CV RGB & GRAY imgs
        self.cv_rgb = cv.cvtColor(self.frame, cv.COLOR_BGR2RGB)
        self.cv_gray = cv.cvtColor(self.frame, cv.COLOR_BGR2GRAY)

    # PROCESSING STAGE
    def _processing_stage(self):
        self.detected_qrcode = self._processing_detect_qrcode()
        self.detected_face = self._processing_detect_face()

        if self.SHOW_PERFORMANCE:
            self._processing_app_performance()

    def _processing_detect_qrcode(self):
        if self.status == StatusFSM.ALLOWED:
            return
        return self.detector_pyzbar.detect_qrcode(self.cv_gray)

    def _processing_detect_face(self):
        match self.FACE_DETECTOR:
            case "Haarcascade":
                cv_frame = self.cv_gray
            case "Blazeface":
                cv_frame = self.cv_rgb
        return self.face_detector.detect_face(cv_frame)

    def _processing_app_performance(self):
        self.performance_params = dict()
        self.performance_params["fps"] = self._processing_fps_performance()
        self.performance_params["FD"] = self.FACE_DETECTOR
        open_cv.output_performance(
            frame=self.frame,
            params=self.performance_params,
            width=self.width,
            height=self.height,
        )

    def _processing_fps_performance(self):
        self.fps += 1
        elapsed_time = time.time() - self.start_time

        if elapsed_time >= 1.0:
            self.fps_calc = self.fps / elapsed_time
            self.fps = 0
            self.start_time = time.time()

        return f"{self.fps_calc:.2f}"

    # POST PROCESSING STAGE
    def _post_processing_stage(self):
        # TODO: #29 `_post_processing_stage` set status, processing `processed_qr_label` & `processed_detected_face`
        if self.detected_qrcode:
            self._post_processing_qrcode()
        elif self.detected_face:
            self._post_processing_face()
        else:
            self._post_processing_nothing()

        self._output_postprocessing()

    def _post_processing_qrcode(self):
        match self.status:
            case (
                StatusFSM.DETECTING,
                StatusFSM.FACE_DETECTED_LEVEL_A,
                StatusFSM.FACE_DETECTED_LEVEL_C,
            ):
                qrcode_label = self._post_processing_decode_qrcode(self.detected_qrcode)
                self.collected_labels.append(qrcode_label)
                self.status = StatusFSM.QRCODE_DETECTED
            case StatusFSM.QRCODE_DETECTED:
                qrcode_label = self._post_processing_decode_qrcode(self.detected_qrcode)
                self.collected_labels.append(qrcode_label)
                if len(self.collected_labels) >= self.LABELS_COUNT:
                    self._post_processing_check_collected_labels()
                else:
                    self.status = StatusFSM.QRCODE_DETECTED
            case StatusFSM.FACE_DETECTED_LEVEL_B:
                self._post_processing_reset_collected_labels()
                qrcode_label = self._post_processing_decode_qrcode(self.detected_qrcode)
                self.collected_labels.append(qrcode_label)
                self.status = StatusFSM.QRCODE_DETECTED
            case StatusFSM.NOT_ALLOWED:
                qrcode_label = self._post_processing_decode_qrcode(self.detected_qrcode)
                self._post_processing_check_not_allowed_label(qrcode_label)

    def _post_processing_face(self):
        if self.status == StatusFSM.QRCODE_DETECTED:
            self._post_processing_reset_collected_labels()

        facearea = self.detected_face.area
        if facearea < self.FACEAREA_LEVEL_B:
            self.__post_processing_face_level_a()
        elif self.FACEAREA_LEVEL_B <= facearea < self.FACEAREA_LEVEL_C:
            self.__post_processing_face_level_b()
        else:
            self.__post_processing_face_level_c()

    def _post_processing_nothing(self):
        match self.status:
            case (
                StatusFSM.DETECTING,
                StatusFSM.FACE_DETECTED_LEVEL_A,
                StatusFSM.FACE_DETECTED_LEVEL_C,
            ):
                self.status = StatusFSM.DETECTING
            case (
                StatusFSM.QRCODE_DETECTED,
                StatusFSM.FACE_DETECTED_LEVEL_B,
            ):
                self._post_processing_reset_collected_labels()
                self.status = StatusFSM.DETECTING
            case StatusFSM.ALLOWED:
                self._post_processing_check_allowed_status()
            case StatusFSM.NOT_ALLOWED:
                self._post_processing_check_not_allowed_time()

    def _post_processing_decode_qrcode(self, detected_qrcode):
        self._draw_detected_qrcode(self.detected_qrcode)
        return self.detector_pyzbar.decode_qrcode(detected_qrcode)

    def _post_processing_reset_collected_labels(self):
        self.guest_recognition_iteration = 0
        self.collected_labels = []

    def _post_processing_check_allowed_status(self):
        if self.start_passage_time:
            self._post_processing_check_passage_time()
        else:
            self._post_processing_check_allowed_time()

    def _post_processing_check_allowed_time(self):
        allowed_time = time.time() - self.start_allowed_time
        if allowed_time >= self.ALLOWED_TIME_SEC:
            self._post_processing_close_gate()
        else:
            self._post_processing_passage_face()

    def _post_processing_check_passage_time(self):
        passage_time = time.time() - self.start_passage_time
        if passage_time >= self.PASSAGE_TIME_SEC:
            self._post_processing_close_gate()
        else:
            self.status = StatusFSM.ALLOWED

    def _post_processing_passage_face(self):
        # TODO: #30 Passage on right side case
        if not self.detected_face:
            self.status = StatusFSM.ALLOWED
        elif (self.detected_face.rect[0] < 15) and (
            self.detected_face.area > 250
        ):  # TODO: #31 Passage face area settings
            self.start_passage_time = time.time()
            self.status = StatusFSM.ALLOWED
        else:
            self.status = StatusFSM.ALLOWED

    def _post_processing_close_gate(self):
        self.turnstile_gpio.close_gate()
        self.status = StatusFSM.DETECTING

    def _post_processing_check_not_allowed_label(self, label):
        if label == self.label_not_allowed:
            self._post_processing_check_not_allowed_time()
        else:
            self.status = StatusFSM.DETECTING

    def _post_processing_check_not_allowed_time(self):
        not_allowed_time = time.time() - self.start_not_allowed_time
        if not_allowed_time >= self.NOT_ALLOWED_TIME_SEC:
            self.status = StatusFSM.DETECTING
        else:
            self.status = StatusFSM.NOT_ALLOWED

    def _post_processing_check_collected_labels(self):
        if frequent_label := self._post_processing_frequent_label():
            self._post_processing_check_skipass(frequent_label)
        else:
            self._post_processing_check_iteration(frequent_label)

    def _post_processing_check_skipass(self, frequent_label):
        if skipass := self._post_processing_db_skipasses(frequent_label):
            self._post_processing_open_gate()
        else:
            self._post_processing_check_iteration(frequent_label)

    def _post_processing_open_gate(self):
        self.turnstile_gpio.open_gate()
        self.start_allowed_time = time.time()
        self.status = StatusFSM.ALLOWED

    def _post_processing_db_skipass(self, frequent_label):
        cursor = database.get_cursor()
        table = "skipass"
        datetime = f"datetime({time.time()},'unixepoch', 'localtime')"
        select_condition = f"SELECT * FROM {table}"
        where_condition = f"""
        WHERE label = {frequent_label}
        AND start_slot <= {datetime}
        AND end_slot >= {datetime}"""
        sql = f"{select_condition} {where_condition}"
        cursor.execute(sql)
        return cursor.fetchone()

    def _post_processing_check_iteration(self, frequent_label):
        if self.guest_recognition_iteration < self.ITERATION_COUNT:
            self.guest_recognition_iteration += 1
            self.status = StatusFSM.DETECTING
        else:
            self._post_processing_reset_collected_labels()
            self.start_not_allowed_time = time.time()
            self.label_not_allowed = frequent_label
            self.status = StatusFSM.NOT_ALLOWED

    def _post_processing_frequent_label(self):
        collected_labels = self.collected_labels
        self._post_processing_reset_collected_labels()
        frequent_label = max(set(collected_labels), key=collected_labels.count)
        return (
            frequent_label
            if collected_labels.count(frequent_label) >= self.REQUIRED_QUANTITY
            else None
        )

    def __post_processing_face_level_a(self):
        match self.status:
            case (
                StatusFSM.DETECTING,
                StatusFSM.QRCODE_DETECTED,
                StatusFSM.FACE_DETECTED_LEVEL_A,
                StatusFSM.FACE_DETECTED_LEVEL_C,
            ):
                # TODO: calculate difference to Level B
                self.status = StatusFSM.FACE_DETECTED_LEVEL_A
            case StatusFSM.FACE_DETECTED_LEVEL_B:
                self._post_processing_reset_collected_labels()
                # TODO: calculate difference to Level B
                self.status = StatusFSM.FACE_DETECTED_LEVEL_A
            case StatusFSM.ALLOWED:
                self._post_processing_check_allowed_status()
            case StatusFSM.NOT_ALLOWED:
                self._post_processing_check_not_allowed_time()

    def __post_processing_face_level_b(self):
        match self.status:
            case (
                StatusFSM.DETECTING,
                StatusFSM.QRCODE_DETECTED,
                StatusFSM.FACE_DETECTED_LEVEL_A,
                StatusFSM.FACE_DETECTED_LEVEL_C,
            ):
                face_label = self._post_processing_face_recognition(
                    self.detected_face.rect
                )
                self.collected_labels.append(face_label)
                self.status = StatusFSM.FACE_DETECTED_LEVEL_B
            case StatusFSM.FACE_DETECTED_LEVEL_B:
                face_label = self._post_processing_face_recognition(
                    self.detected_face.rect
                )
                self.collected_labels.append(face_label)
                if len(self.collected_labels) >= self.LABELS_COUNT:
                    self._post_processing_check_collected_labels()
                else:
                    self.status = StatusFSM.FACE_DETECTED_LEVEL_B

            case StatusFSM.ALLOWED:
                self._post_processing_check_allowed_status()
            case StatusFSM.NOT_ALLOWED:
                face_label = self._post_processing_face_recognition(
                    self.detected_face.rect
                )
                self._post_processing_check_not_allowed_label(face_label)

    def __post_processing_face_level_c(self):
        match self.status:
            case (
                StatusFSM.DETECTING,
                StatusFSM.QRCODE_DETECTED,
                StatusFSM.FACE_DETECTED_LEVEL_A,
                StatusFSM.FACE_DETECTED_LEVEL_C,
            ):
                # TODO: calculate difference to Level B
                self.status = StatusFSM.FACE_DETECTED_LEVEL_C
            case StatusFSM.FACE_DETECTED_LEVEL_B:
                self._post_processing_reset_collected_labels()
                # TODO: calculate difference to Level B
                self.status = StatusFSM.FACE_DETECTED_LEVEL_C
            case StatusFSM.ALLOWED:
                self._post_processing_check_allowed_status()
            case StatusFSM.NOT_ALLOWED:
                self.status = StatusFSM.DETECTING

    def _post_processing_face_recognition(self, face_coords):
        ypred = self.embedder.get_embeddings(face_coords, self.cv_rgb)
        face_label = self.svm_model.predict(ypred)
        return self.label_encoder.inverse_transform(face_label)[0]

    def _draw_detected_qrcode(self, detected_qrcode):
        qrcode_rect = self.detector_pyzbar.get_coords_qrcode(detected_qrcode)
        open_cv.output_qrcode(qrcode_rect)

    def _face_recognition(self, face_coords):
        ypred = self.embedder.get_embeddings(face_coords, self.cv_rgb)
        face_name = self.svm_model.predict(ypred)
        label = self.label_encoder.inverse_transform(face_name)[0]

    def _collect_label(self, label):
        self.collected_labels.append(label)
        if len(self.collected_labels) >= self.LABELS_COUNT:
            frequent_label = self._get_frequent_label()

            if not frequent_label:
                self.collected_labels = []
                self._check_guest_recognition_iteration()

            # TODO: Check DB
            self.passage_label = frequent_label

    def _check_guest_recognition_iteration(self):
        if self.guest_recognition_iteration > self.ITERATION_COUNT:
            self.status = StatusFSM.NOT_ALLOWED
            self.guest_recognition_iteration = 0
        else:
            self.guest_recognition_iteration += 1

    # def _get_skipasses_by_label()

    ########## REF UP ##########

    def _checking_time_allowed(self):
        if not self.start_allowed_time:
            self.start_allowed_time = time.time()
            self.turnstile_gpio.open_gate()
            return

        checking_time = time.time() - self.start_allowed_time
        if checking_time >= 4:  # TODO: instead `10` second - diffrent value from `_set`
            self._reset_guest_recognition()
            self.turnstile_gpio.close_gate()

    def _reset_guest_recognition(self):
        self.status = StatusFSM.SEARCHING
        self.collected_labels = []
        self.passage_label = None
        self.start_allowed_time = None

    def _load_ml_data(self):
        self.svm_model = pickle.load(open(_set.data.svm_model_path, "rb"))
        self.faces_embeddings = np.load(_set.data.embeddings_path)
        Y = self.faces_embeddings["arr_1"]
        self.label_encoder.fit(Y)
        self.status = StatusFSM.DETECTING

    def _draw_detect_face(self, detected_face):
        open_cv.output_face(
            frame=self.frame,
            face=detected_face,
            level_b=self.LEVEL_B,
            level_c=self.LEVEL_C,
            show_performance=self.SHOW_PERFORMANCE,
        )

    def _set_app_settings(self):
        app_settings = database.fetchall(
            table="app_settings",
            columns=[
                "gr_face_detector",
                "gr_level_a_side",
                "gr_level_b_side",
                "gr_level_c_side",
                "gr_labels_count",
                "gr_percent_required",
                "gr_iteration_count",
                "gr_allowed_time_sec",
                "gr_passage_time_sec",
                "gr_not_allowed_time_sec" "show_performance",
            ],
        )[0]

        self._set_face_detector(int(app_settings.get("gr_face_detector")))

        self.FACEAREA_LEVEL_A = int(app_settings.get("gr_level_a_side")) ** 2
        self.FACEAREA_LEVEL_B = int(app_settings.get("gr_level_b_side")) ** 2
        self.FACEAREA_LEVEL_C = int(app_settings.get("gr_level_c_side")) ** 2
        self.LABELS_COUNT = int(app_settings.get("gr_labels_count"))
        self.PERCENT_REQUIRED = int(app_settings.get("gr_percent_required"))
        self.REQUIRED_QUANTITY = int(self.LABELS_COUNT * self.PERCENT_REQUIRED / 100)
        self.ITERATION_COUNT = int(app_settings.get("gr_iteration_count"))
        self.ALLOWED_TIME_SEC = int(app_settings.get("gr_allowed_time_sec"))
        self.PASSAGE_TIME_SEC = int(app_settings.get("gr_passage_time_sec"))
        self.NOT_ALLOWED_TIME_SEC = int(app_settings.get("gr_not_allowed_time_sec"))
        self.SHOW_PERFORMANCE = bool(app_settings.get("show_performance"))

    def _set_face_detector(self, gr_face_detector):
        """
        Set Face Detector by `gr_face_detector`:
        - 0: Haarcascade
        - 1: Blazeface
        """
        match gr_face_detector:
            case 0:
                self.face_detector = self.detector_haarcascade
                self.FACE_DETECTOR = "Haarcascade"
            case 1:
                self.face_detector = self.detector_blazeface
                self.FACE_DETECTOR = "Blazeface"
