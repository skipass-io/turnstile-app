import io
import random
import time
from PIL import Image

from core import settings
from core.schemas import TurnstileSettings
from guest_recognition import StatusFSM
from guest_recognition.actions import DB, Server
from guest_recognition.detectors import DetectorPyzbar
from guest_recognition.utils import FPS, OpenCV, TurnstileGPIO


class PostProcessing:
    def __init__(self):
        # Detectors
        self.pyzbar = DetectorPyzbar()

        # Actions
        self.db = DB()
        self.server = Server(token=self.db.get_token())

        # Utils
        self.fps = FPS()
        self.open_cv = OpenCV()
        self.gpio = TurnstileGPIO()

        # Post Processing Data Input
        self.width = None
        self.height = None
        self.token = None  #  for now, need to change
        self.detected_face = None
        self.passage_start = None
        self.passage_time = None
        self.PASSAGE_TIME_LIMIT = settings.turnstile.passage_time_limit
        self.face_frames = []
        self.FACE_FRAMES_COUNT = None

        self.turnstile_settings: TurnstileSettings = TurnstileSettings(
            **settings.turnstile.default.model_dump()
        )

        # Post Processing Data Output
        self.status = None
        self.progress = None

    def stage(
        self,
        status,
        width,
        height,
        frame,
        cv_gray,
        cv_rgb,
        detected_qrcode,
        detected_face,
    ):
        self._set_data_input(
            width=width,
            height=height,
            frame=frame,
            cv_gray=cv_gray,
            cv_rgb=cv_rgb,
            detected_qrcode=detected_qrcode,
            detected_face=detected_face,
        )
        if self.detected_qrcode:
            self._stage_qrcode(status=status, detected_qrcode=detected_qrcode)
        elif detected_face:
            self._stage_face()
        else:
            self._stage_nothing()

        if self.turnstile_settings.show_perfomance:
            self._stage_perfomance()

    # STAGE_PART
    def _stage_qrcode(self, status, detected_qrcode):
        match status:
            case StatusFSM.NOT_ACTIVE:
                qrcode_token = self.pyzbar.decode_qrcode(detected_qrcode)
                if turnstile_settings := self.server.turnstile_active(
                    token=qrcode_token
                ):
                    self.db.set_token(token=qrcode_token)
                    self._set_turnstile_settings_update(
                        turnstile_settings_update=turnstile_settings
                    )
                    self._set_status_and_progress(
                        status=StatusFSM.DETECTING,
                    )
                else:
                    self._set_status_and_progress(
                        status=StatusFSM.NOT_ACTIVE,
                    )

    def _stage_face(self, status, detected_face):
        self.detected_face = detected_face
        if self.detected_face["area"] < self.turnstile_settings.gr_level_b:
            self._stage_face_level_a()
        elif (
            self.turnstile_settings.gr_level_b
            <= self.detected_face["area"]
            < self.turnstile_settings.gr_level_c
        ):
            self._stage_face_level_b()
        else:
            self._stage_face_level_c()

    def _stage_face_level_a(self, status):
        # Get Closer
        match status:
            case (
                StatusFSM.DETECTING
                | StatusFSM.FACE_DETECTED_LEVEL_A
                | StatusFSM.FACE_DETECTED_LEVEL_C
                # | StatusFSM.QRCODE_DETECTED TODO: add QRCODE Acts
            ):
                self._set_status_and_progress(
                    status=StatusFSM.FACE_DETECTED_LEVEL_A,
                    progress=int(
                        self.detected_face["area"]
                        / self.turnstile_settings.gr_level_b
                        * 100
                    ),
                )

            case StatusFSM.FACE_DETECTED_LEVEL_B:
                self.face_frames = []  # full reset
                self._set_status_and_progress(
                    status=StatusFSM.FACE_DETECTED_LEVEL_A,
                    progress=int(
                        self.detected_face["area"]
                        / self.turnstile_settings.gr_level_b
                        * 100
                    ),
                )
            case StatusFSM.ALLOWED:
                self._stage_check_allowed_status()
            case StatusFSM.NOT_ALLOWED:
                self._stage_check_not_allowed_time()

    def _stage_face_level_b(self, status):
        match status:
            case (
                StatusFSM.DETECTING
                | StatusFSM.FACE_DETECTED_LEVEL_A
                | StatusFSM.FACE_DETECTED_LEVEL_C
                # | StatusFSM.QRCODE_DETECTED TODO: add QRCODE Acts
            ):
                self._utils_set_face_frames_count()
                self._set_status_and_progress(
                    status=StatusFSM.FACE_DETECTED_LEVEL_B,
                )
            case StatusFSM.FACE_DETECTED_LEVEL_B:

                face_frame = self._utils_face_frame_extract(
                    self.cv_rgb, self.detected_face["rect"]
                )
                self.face_frames.append(face_frame)

                if len(self.face_frames) >= self.FACE_FRAMES_COUNT:
                    self._server_passage_request()
                else:
                    self._set_status_and_progress(
                        status=StatusFSM.FACE_DETECTED_LEVEL_B,
                        progress=int(
                            len(self.face_frames)
                            / self.FACE_FRAMES_COUNT
                            * 90  # <- for pending
                        ),
                    )

            case StatusFSM.ALLOWED:
                self._stage_check_allowed_status()
            case StatusFSM.NOT_ALLOWED:
                self._stage_check_not_allowed_time()

    def _stage_face_level_c(self, status):
        match status:
            case (
                StatusFSM.DETECTING
                | StatusFSM.FACE_DETECTED_LEVEL_A
                | StatusFSM.FACE_DETECTED_LEVEL_C
                # | StatusFSM.QRCODE_DETECTED TODO: add QRCODE Acts
            ):
                self._set_status_and_progress(
                    status=StatusFSM.FACE_DETECTED_LEVEL_C,
                    progress=int(
                        self.turnstile_settings.gr_level_c
                        / self.detected_face["area"]
                        * 100
                    ),
                )

            case StatusFSM.FACE_DETECTED_LEVEL_B:
                self.face_frames = []  # full reset
                self._set_status_and_progress(
                    status=StatusFSM.FACE_DETECTED_LEVEL_C,
                    progress=int(
                        self.turnstile_settings.gr_level_c
                        / self.detected_face["area"]
                        * 100
                    ),
                )
            case StatusFSM.ALLOWED:
                self._stage_check_allowed_status()
            case StatusFSM.NOT_ALLOWED:
                self._stage_check_not_allowed_time()

    def _stage_nothing(self, status):
        # TODO: give turnstile state to server
        match status:
            case StatusFSM.NOT_ACTIVE:
                if turnstile_settings := self.server.turnstile_active():
                    self.turnstile_settings = turnstile_settings
                    self._set_status_and_progress(
                        status=StatusFSM.DETECTING,
                    )
                else:
                    self._set_status_and_progress(
                        status=StatusFSM.NOT_ACTIVE,
                    )
            case (
                StatusFSM.DETECTING
                | StatusFSM.FACE_DETECTED_LEVEL_A
                | StatusFSM.FACE_DETECTED_LEVEL_C
            ):
                self._set_status_and_progress(
                    status=StatusFSM.DETECTING,
                )
            case StatusFSM.QRCODE_DETECTED | StatusFSM.FACE_DETECTED_LEVEL_B:
                self.face_frames = []  # full reset
                self._set_status_and_progress(
                    status=StatusFSM.DETECTING,
                )
            case StatusFSM.ALLOWED:
                self._post_processing_check_allowed_status()
            case StatusFSM.NOT_ALLOWED:
                self._post_processing_check_not_allowed_time()

    def _stage_perfomance(self):
        performance_params = dict()
        performance_params["fps"] = self.fps.fps
        performance_params["brt"] = self.open_cv.get_brightness(frame=self.frame)

        self.open_cv.output_performance(
            frame=self.frame,
            params=performance_params,
            width=self.width,
            height=self.height,
        )

    def _stage_check_allowed_status(self):
        passing_time = time.time() - self.passage_time

        if passing_time >= self.PASSAGE_TIME_LIMIT:
            self._turnstile_close_gate()
            self._set_status_and_progress(
                status=StatusFSM.DETECTING,
            )
        else:
            self._set_status_and_progress(
                status=StatusFSM.ALLOWED,
                progress=int(passing_time / self.PASSAGE_TIME_LIMIT * 100),
            )

    def _stage_check_not_allowed_time(self):
        passing_time = time.time() - self.passage_time

        if passing_time >= self.PASSAGE_TIME_LIMIT:
            self._set_status_and_progress(
                status=StatusFSM.DETECTING,
            )
        else:
            self._set_status_and_progress(
                status=StatusFSM.NOT_ALLOWED,
                progress=int(passing_time / self.PASSAGE_TIME_LIMIT * 100),
            )

    # SET_PART
    def _set_data_input(
        self,
        width,
        height,
        frame,
        cv_gray,
        cv_rgb,
        detected_qrcode,
        detected_face,
    ):
        # Data Input
        self.width = width
        self.height = height
        self.frame = frame
        self.cv_gray = cv_gray
        self.cv_rgb = cv_rgb
        self.detected_qrcode = detected_qrcode
        self.detected_face = detected_face

        # Utils
        self.fps.get_frames_per_second()

    def _set_turnstile_settings_update(self, turnstile_settings_update):
        for name, value in turnstile_settings_update.model_dump(
            exclude_unset=True
        ).items():
            setattr(self.turnstile_settings, name, value)

    def _set_status_and_progress(self, status, progress=0):
        self.status = status
        self.progress = progress

    # SERVER_PART
    def _server_passage_request(self):
        passage = self.server.turnstile_passage(
            frames=self._utils_get_frames_for_request()
        )

        if passage is None:
            # TODO: if server let down
            print("passage request is None")
            self._set_status_and_progress(
                status=StatusFSM.DETECTING,  #  <- There should be an another status
            )
            return

        self._turnstile_passage_access(passage)

        self.db.set_passage(
            passage_id=passage.id,
            passage_duration=self._turnstile_passage_duration(),
        )

    # TURNSTILE_PART
    def _turnstile_passage_access(self, passage):
        if passage.access:
            self._turstile_open_gate()
            self._set_status_and_progress(
                status=StatusFSM.ALLOWED,
            )
        else:
            self._set_status_and_progress(
                status=StatusFSM.NOT_ALLOWED,
            )

    def _turnstile_passage_duration(self):
        passage_end = time.time()
        passage_duration = int(self.passage_start - passage_end)
        return passage_duration

    def _turstile_open_gate(self):
        self.gpio.open_gate()
        self.passage_time = time.time()

    def _turnstile_close_gate(self):
        self.gpio.close_gate()

    # UTILS_PART
    def _utils_set_face_frames_count(self):
        self.passage_start = time.time()
        self.FACE_FRAMES_COUNT = int(
            self.fps.fps * 0.8
        )  # <- 80% of perfomance in 1 sec

    def _utils_face_frame_extract(self, cv_rgb, detected_face):
        x, y, w, h = detected_face["rect"]
        return cv_rgb[y : y + h, x : x + w]

    def _utils_get_frames_for_request(self):
        k = int(len(self.face_frames) * 0.25)
        faces = random.sample(population=self.face_frames, k=k)
        frames = []
        for face in faces:
            pil_img = Image.fromarray(face)
            buf = io.BytesIO()
            pil_img.save(buf, format="PNG")
            frames.append(buf.getvalue())
        return frames
