import cv2 as cv

from core import settings
from guest_recognition.status_fsm import StatusFSM
from guest_recognition.detectors import DetectorPyzbar, DetectorHaarcascade
from guest_recognition.utils import OpenCV


class Processing:
    def __init__(self):
        # Detectors
        self.pyzbar = DetectorPyzbar()
        self.haarcascade = DetectorHaarcascade(
            haarcascade_file=str(settings.fd.haarcascade_path),
            scale_factor=settings.fd.scale_factor,
            min_neighbors=settings.fd.min_neighbors,
            min_size=(136, 136),
        )

        # Utils
        self.open_cv = OpenCV()

        # Processing Data Input
        self.status = None
        self.frame = None
        self.cv_gray = None

        # Processing Data Output
        self.detected_qrcode = None
        self.detected_face = None

    def stage(self, status, frame, cv_gray):
        self._set_data_input(
            status=status,
            frame=frame,
            cv_gray=cv_gray,
        )

        self.detected_qrcode = self._detect_qrcode()
        self.detected_face = self._detect_face()

        if self.detected_qrcode:
            self._show_detected_qrcode()
        if self.detected_face:
            self._show_detected_face()

    def _set_data_input(
        self,
        status,
        frame,
        cv_gray,
    ):
        self.status = status
        self.frame = frame
        self.cv_gray = cv_gray

    def _detect_qrcode(self):
        # if self.status != StatusFSM.NOT_ACTIVE:
        #     return

        return self.pyzbar.detect_qrcode(self.cv_gray)

    def _detect_face(self):
        if self.status == StatusFSM.NOT_ACTIVE:
            return

        return self.haarcascade.detect_face(self.cv_gray)

    def _show_detected_qrcode(self):
        qrcode_rect = self.pyzbar.get_coords_qrcode(self.detected_qrcode)
        self.open_cv.output_qrcode(
            frame=self.frame,
            qrcode_rect=qrcode_rect,
        )

    def _show_detected_face(self):
        self.open_cv.output_face(
            frame=self.frame,
            face=self.detected_face,
        )
