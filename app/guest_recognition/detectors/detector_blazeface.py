import functools
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class DetectorBlazeface:
    def __init__(self, model_asset_path):
        self.detector = self._get_detector()
        self.model_asset_path = model_asset_path
        self.running_mode = (vision.RunningMode.LIVE_STREAM,)
        # TODO: #15 Create params: `min_detection_confidence`, `min_suppression_threshold` in settings for `DetectorBlazeface`
        self.min_detection_confidence = 0.85
        self.min_suppression_threshold = 0.3

    def detect_face(self, cv_rgb):
        """
        Face detection (Blazeface) on the frame
        (if there is more than one face,
        the largest one / closest to the frame will be returned)
        """
        mp_image = self._image_preprocessing(cv_rgb)
        detected_faces = self._detect_faces(mp_image)
        if len(detected_faces) == 0:
            return
        rect = self._get_face_rect(detected_faces)
        detected_face = {"rect": rect, "area": rect[2] * rect[3]}
        return detected_face

    def _get_detector(self):
        """
        Setting up the MediaPipe Blazeface detector
        """
        base_options = python.BaseOptions(model_asset_path=self.model_asset_path)

        options = vision.FaceDetectorOptions(
            base_options=base_options,
            running_mode=self.running_mode,
            min_detection_confidence=self.min_detection_confidence,
            min_suppression_threshold=self.min_suppression_threshold,
        )
        detector = vision.FaceDetector.create_from_options(options)
        return detector

    def _image_preprocessing(self, cv_rgb):
        """
        Setting frame image for the MediaPipe Blazeface detector
        """
        mp_image = np.array(cv_rgb)
        return mp_image

    def _detect_faces(self, mp_image):
        """
        Detect faces by MediaPipe Blazeface detector on frame preprocessed image
        """
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=mp_image)
        detection_result = self.detector.detect(image)
        return detection_result["detections"]

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
                    if (self._rect_area(face_a)) > (self._rect_area(face_b))
                    else face_b
                ),
                detected_faces,
            )
        return self._face_detection_processing(detected_face)

    def _rect_area(self, detection):
        """
        Returns rect area of detected face on frame
        """
        box = detection.bounding_box
        return box.width * box.height

    def _face_detection_processing(self, detection):
        """
        Returns coords, width & height rect of detected face on frame
        """
        box = detection.bounding_box
        return [box.origin_x, box.origin_y, box.width, box.height]
