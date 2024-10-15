import cv2 as cv

from config import GuestRecognitionSettings


_settings = GuestRecognitionSettings()


class GuestRecognition:
    def __init__(self, frame_size):
        if (not frame_size) or (len(frame_size) != 2):
            raise Exception("Need correct frame_size")

        self.status = None
        self.frame = None
        self.width = frame_size[0]
        self.height = frame_size[1]
        self.cv_rgb = None
        self.cv_gray = None
        self.face_detector = cv.CascadeClassifier(_settings.haarcascade_path)

    def set_frame(self, mapped_array):
        self.frame = mapped_array.array
        self.cv_rgb = self._cv_img("rgb")
        self.cv_gray = self._cv_img("gray")
        self.status = "set_frame"

    def find_faces(self):
        if not self.status == "set_frame":
            raise Exception("Not sef_frame status")

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
        self._show_found_faces(found_faces)

    def _show_found_faces(self, found_faces):
        for x, y, w, h in found_faces:
            cv.rectangle(self.frame, (x, y), (x + w, y + h), (255, 0, 0), 4)

    def _cv_img(self, color):
        match color:
            case "rgb":
                cv_color = cv.COLOR_BGR2RGB
            case "gray":
                cv_color = cv.COLOR_BGR2GRAY
            case _:
                raise Exception("Need color for get_cv_img: gray or rgb")
        return cv.cvtColor(self.frame, cv_color)
