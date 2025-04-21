import functools
import math
import time

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class DetectorBlazeface:
    def __init__(
        self,
        blazeface_path,
        min_detection_confidence,
        min_suppression_threshold,
    ) -> None:
        self.base_options = python.BaseOptions(model_asset_path=str(blazeface_path))
        self.options = vision.FaceDetectorOptions(
            base_options=self.base_options,
            running_mode=vision.RunningMode.LIVE_STREAM,
            min_detection_confidence=min_detection_confidence,
            min_suppression_threshold=min_suppression_threshold,
            result_callback=self._save_result,
        )
        self.detector = vision.FaceDetector.create_from_options(self.options)

        self.DETECTION_RESULT = None

    def _save_result(self, result, unused_output_image, timestamp_ms):
        self.DETECTION_RESULT = result

    def detect_face(self, mp_image):
        self.detector.detect_async(mp_image, time.time_ns() // 1_000_000)
        return self._get_detection_result()

    def _get_detection_result(self):
        if not self.DETECTION_RESULT:
            return
        detections = self.DETECTION_RESULT.detections
        if not detections:
            return
        rect = self._get_face_rect(detections)

        return {"rect": rect, "side": int(math.sqrt(rect[2] * rect[3]))}

    def _get_face_rect(self, detections):
        if len(detections) == 1:
            detected_face = detections[0]
        else:
            detected_face = functools.reduce(
                lambda detection_a, detection_b: (
                    detection_a
                    if (
                        detection_a.bounding_box.width * detection_a.bounding_box.height
                    )
                    > (detection_b.bounding_box.width * detection_b.bounding_box.height)
                    else detection_b
                ),
                detections,
            )
        print(detected_face)
        return [
            detected_face.bounding_box.origin_x,
            detected_face.bounding_box.origin_y,
            detected_face.bounding_box.width,
            detected_face.bounding_box.height,
        ]
