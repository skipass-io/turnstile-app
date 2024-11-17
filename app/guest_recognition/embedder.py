import cv2 as cv
import numpy as np
from keras_facenet import FaceNet


class Embedder:
    def __init__(self):
        self.embedder = FaceNet()

    def get_embeddings(self, face_coords, cv_rgb):
        """
        Get embeddings from detected face on the frame
        """
        face_img = self._image_preprocessing(face_coords, cv_rgb)
        ypred = self.facenet.embeddings(face_img)
        return ypred

    def _image_preprocessing(self, face_coords, cv_rgb):
        """
        Preprocessing of the frame image to getting embedings
        """
        x, y, w, h = face_coords
        face_img = cv_rgb[y : y + h, x : x + w]
        face_img = cv.resize(face_img, (160, 160))
        face_img = np.expand_dims(face_img, axis=0)
        return face_img
