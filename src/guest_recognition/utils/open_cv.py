import math
import cv2 as cv
import numpy as np


class OpenCV:
    def __init__(self):
        pass

    def output_performance(
        self,
        frame,
        params,
        width,
        height,
    ):
        performance = ", ".join(f"{key}: {value}" for key, value in params.items())
        cv.putText(
            frame,
            performance,
            (10, height - 30),
            cv.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            3,
            cv.LINE_AA,
        )

    def get_brightness(self, frame):
        """Calculate the average brightness of the image."""
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        return round(np.mean(gray), 2)

    def output_face(
        self,
        frame,
        face,
    ):
        x, y, w, h = face["rect"]
        facearea = face["area"]
        faceside = int(math.sqrt(facearea))
        color = (194, 51, 255)  # Pink
        thinkness = 4

        cv.rectangle(frame, (x, y), (x + w, y + h), color, thinkness)

    def output_qrcode(
        self,
        frame,
        qrcode_rect,
    ):
        x, y, w, h = qrcode_rect
        color = (194, 51, 255)  # Pink
        thinkness = 4
        cv.rectangle(frame, (x, y), (x + w, y + h), color, thinkness)
