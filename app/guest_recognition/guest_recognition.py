import pickle

import cv2 as cv
import numpy as np
from keras_facenet import FaceNet
from sklearn.preprocessing import LabelEncoder
from pyzbar.pyzbar import decode as pyzbar_decoder
from pyzbar.pyzbar import Decoded as PyzbarDecoded

from core.config import GuestRecognitionSettings
from .exceptions import NotCorrectStatusGR, NotCorrectFrameSizeGR
from .statuses import StatusGR


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
        self.status = StatusGR.GET_READY

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
        self._check_correct_status(
            correct_statuses=[StatusGR.GET_READY]
        )  # TODO: think about array of complited statuses ot smths

        self.frame = mapped_array.array
        self.cv_rgb = self._cv_img("rgb")
        self.cv_gray = self._cv_img("gray")

    def _find_qrcodes(self):
        self._check_correct_status(correct_statuses=[StatusGR.GET_READY])

        codes = self.qr_decoder(self.cv_gray)
        self._draw_rectangles(
            codes, _settings.colors.BLUE_RBG
        )  # TODO: remove drawing for all qr_codes, replace draw for each qr_code

    def _find_faces(self):
        self._check_correct_status(correct_statuses=[StatusGR.GET_READY])
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
        self._draw_rectangles(
            found_faces, _settings.colors.DARK_BLUE_RGB
        )  # TODO: remove drawing for all faces, replace draw for each face
        for face in found_faces:
            x, y, w, h = face
            if (w > (self.width / 2)) & (h > (self.height / 2)):
                self._face_recognition(
                    face_coords=face
                )  # TODO: instead "2" - scalar_face_recognition in _settings
            else:
                print("Small face")  # TODO: remove, add some business logic

    def _face_recognition(self, face_coords):
        x, y, w, h = face_coords
        face_img = self.cv_rgb[y : y + h, x : x + w]
        face_img = cv.resize(face_img, (160, 160))
        face_img = np.expand_dims(face_img, axis=0)
        ypred = self.facenet.embeddings(face_img)
        face_name = self.svm_model.predict(ypred)
        label = self.label_encoder.inverse_transform(face_name)[0]
        print("facenet label:", label)  # TODO: remove, collect labels

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
