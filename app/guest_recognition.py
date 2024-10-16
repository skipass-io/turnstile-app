import pickle

import cv2 as cv
import numpy as np
from keras_facenet import FaceNet
from sklearn.preprocessing import LabelEncoder
from pyzbar.pyzbar import decode as pyzbar_decoder
from pyzbar.pyzbar import Decoded as PyzbarDecoded

from config import GuestRecognitionSettings
from exceptions import NotCorrectStatusGR, NotCorrectFrameSizeGR


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
        self.svm_model = pickle.load(open(_settings.svm_model_path, "rb"))
        self.faces_embeddings = np.load(_settings.embeddings_path)
        Y = self.faces_embeddings["arr_1"]
        self.label_encoder.fit(Y)
        self.status = "loaded_data_for_ml"

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
        self._check_correct_status(correct_statuses=["loaded_data_for_ml"])

        self.frame = mapped_array.array
        self.cv_rgb = self._cv_img("rgb")
        self.cv_gray = self._cv_img("gray")
        self.status = "set_frame"

    def _find_qrcodes(self):
        self._check_correct_status(correct_statuses=["set_frame"])

        codes = self.qr_decoder(self.cv_gray)
        self._draw_rectangles(codes, _settings.colors.BLUE_RBG)

    def _find_faces(self):
        self._check_correct_status(correct_statuses=["set_frame"])
        fd_settings = _settings.face_detector_settings

        found_faces = self.face_detector.detectMultiScale(
            image=self.cv_gray,
            scaleFactor=fd_settings.scale_factor,
            minNeighbors=fd_settings.min_neighbors,
            minSize=(
                int(self.width / fd_settings.scalar_face_detect),
                int(self.height / fd_settings.scalar_face_detect),
            ),
        )
        self._draw_rectangles(found_faces, _settings.colors.DARK_BLUE_RGB)

    def _draw_rectangles(self, objects, color_rgb=(255, 255, 255)):
        for obj in objects:
            if isinstance(obj, PyzbarDecoded):
                obj = obj.rect
            x, y, w, h = obj
            cv.rectangle(self.frame, (x, y), (x + w, y + h), color_rgb, 4)

    def run(self, mapped_array):
        """Processing PiCamera frame"""
        self._set_frame(mapped_array)
        self._find_qrcodes()
        self._find_faces()

    def __init__(self, frame_size):
        if (not frame_size) or (len(frame_size) != 2):
            raise NotCorrectFrameSizeGR(frame_size=frame_size)

        self.status = None
        self.frame = None
        self.width = frame_size[0]
        self.height = frame_size[1]
        self.cv_rgb = None
        self.cv_gray = None
        self.face_detector = cv.CascadeClassifier(_settings.haarcascade_path)
        self.qr_decoder = pyzbar_decoder
        self.label_encoder = LabelEncoder()
        self.facenet = FaceNet()
        self.svm_model = None
        self.faces_embeddings = None

        self._load_data_for_ml()
