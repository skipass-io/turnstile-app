import functools
import math
import cv2 as cv


class DetectorHaarcascade:
    def __init__(
        self,
        haarcascade_file,
        scale_factor,
        min_neighbors,
        min_size,
    ):
        # Detector
        self.detector = cv.CascadeClassifier(haarcascade_file)

        # Settings
        self.scale_factor = scale_factor
        self.min_neighbors = min_neighbors
        self.min_size = min_size

    def detect_face(self, cv_gray):
        """
        Face detection (Haarcascade) on the frame
        (if there is more than one face,
        the largest one / closest to the frame will be returned)
        """
        detected_faces = self._detect_faces(cv_gray)
        if len(detected_faces) == 0:
            return
        rect = self._get_face_rect(detected_faces)
        detected_face = {"rect": rect, "side": int(math.sqrt(rect[2] * rect[3]))}
        return detected_face

    def _detect_faces(self, cv_gray):
        """
        Setting up the Haarcascade detector
        and detect faces in the `cv_gray` frame
        """
        return self.detector.detectMultiScale(
            image=cv_gray,
            scaleFactor=self.scale_factor,
            minNeighbors=self.min_neighbors,
            minSize=self.min_size,
        )

    def _get_face_rect(self, detected_faces):
        """
        Returns a detected face from the array of `detected_faces`.
        (if more than one face is detected,
        the one with the larger area will be returned.)
        """
        if len(detected_faces) == 1:
            detected_face = detected_faces[0]
        else:
            detected_face = functools.reduce(
                lambda face_a, face_b: (
                    face_a
                    if (face_a[2] * face_a[3]) > (face_b[2] * face_b[3])
                    else face_b
                ),
                detected_faces,
            )
        return detected_face
