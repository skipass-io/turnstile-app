import cv2 as cv
import numpy as np
from keras_facenet import FaceNet


class Embedder:
    def __init__(self):
        self.embedder = FaceNet()
