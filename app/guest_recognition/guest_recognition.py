import pickle

import cv2 as cv
import numpy as np
from keras_facenet import FaceNet
from sklearn.preprocessing import LabelEncoder
from pyzbar.pyzbar import decode as pyzbar_decoder
from pyzbar.pyzbar import Decoded as PyzbarDecoded

from core.config import GuestRecognitionSettings
from .exceptions import NotCorrectStatusGR, NotCorrectFrameSizeGR
from .status_fsm import StatusFSM


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
        self.status = StatusFSM.GET_READY

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
        self._check_correct_status(correct_statuses=[StatusFSM.GET_READY])

        self.frame = mapped_array.array
        self.cv_rgb = self._cv_img("rgb")
        self.cv_gray = self._cv_img("gray")

    def _find_qrcodes(self):
        self._check_correct_status(correct_statuses=[StatusFSM.GET_READY])

        codes = self.qr_decoder(self.cv_gray)

    def _find_faces(self):
        self._check_correct_status(correct_statuses=[StatusFSM.GET_READY])
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
        for face in found_faces:
            x, y, w, h = face
            if (w > (self.width / fd_settings.scalar_recognition)) & (
                h > (self.height / fd_settings.scalar_recognition)
            ):
                self._face_recognition(face_coords=face)
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

    def _response(self):
        status_text = self.status
        match self.status:
            case StatusFSM.SEARCHING:
                status_hex = _settings.colors.BLUE_HEX
            case StatusFSM.GET_CLOSER:
                status_hex = _settings.colors.BLUE_HEX
            case StatusFSM.QRCODE_SCANNING:
                status_hex = _settings.colors.MAGENTA_HEX
            case StatusFSM.FACE_RECOGNITION:
                status_hex = _settings.colors.MAGENTA_HEX
            case StatusFSM.ALLOWED:
                status_hex = _settings.colors.GREEN_HEX
            case StatusFSM.NOT_ALLOWED:
                status_hex = _settings.colors.RED_HEX
            case StatusFSM.ERROR:
                status_hex = _settings.colors.RED_HEX

        return status_text, status_hex

    def run(self, mapped_array):
        """Processing PiCamera frame"""
        self._set_frame(mapped_array)
        self._find_qrcodes()
        self._find_faces()
        return self._response()

    def __init__(self, frame_size):
        if (not frame_size) or (len(frame_size) != 2):
            raise NotCorrectFrameSizeGR(frame_size=frame_size)

        self.status = None
        self.labels = []
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
