import io
import time
from datetime import datetime
import cv2 as cv

from core import settings
from core.config import BASEDIR
from core.schemas import TurnstileSettings
from guest_recognition.status_fsm import StatusFSM
from guest_recognition.svm_model import SVMModel
from guest_recognition.actions import DB, Server
from guest_recognition.detectors import DetectorPyzbar
from guest_recognition.utils import FPS, OpenCV, TurnstileGPIO


class PostProcessing:
    def __init__(self):
        self.frequent_label = "NONE"
        # SVM Model

        self.svm_model = SVMModel()

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
        self.labels = []
        self.MAX_LABELS_COUNT = settings.turnstile.labels_count
        self.FREQUENT_LABEL_PERCENT = settings.turnstile.frequent_label_percent
        self.passage_frequent_label = None

        self.turnstile_settings_default: TurnstileSettings = TurnstileSettings(
            **settings.turnstile.default.model_dump()
        )

        self.turnstile_settings = self.turnstile_settings_default

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
            detected_face=detected_face,
        )
        if detected_qrcode:
            self._stage_qrcode(
                status=status,
                detected_qrcode=detected_qrcode,
            )
        elif detected_face:
            self._stage_face(
                status=status,
                detected_face=detected_face,
            )
        else:
            self._stage_nothing(
                status=status,
            )

        if self.turnstile_settings.show_performance:
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
                    self.svm_model.download(server=self.server)
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
        if self.detected_face["side"] < self.turnstile_settings.gr_level_b:
            self._stage_face_level_a(status=status)
        elif (
            self.turnstile_settings.gr_level_b
            <= self.detected_face["side"]
            < self.turnstile_settings.gr_level_c
        ):
            self._stage_face_level_b(status=status)
        else:
            self._stage_face_level_c(status=status)

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
                        self.detected_face["side"]  # type: ignore
                        / self.turnstile_settings.gr_level_b
                        * 100
                    ),
                )

            case StatusFSM.FACE_DETECTED_LEVEL_B:
                self._full_reset()
                self._set_status_and_progress(
                    status=StatusFSM.FACE_DETECTED_LEVEL_A,
                    progress=int(
                        self.detected_face["side"]  # type: ignore
                        / self.turnstile_settings.gr_level_b
                        * 100
                    ),
                )
            case StatusFSM.ALLOWED:
                self._stage_check_allowed_status()
            case StatusFSM.NOT_ALLOWED:
                self._stage_check_not_allowed_status()

    def _stage_face_level_b(self, status):
        match status:
            case (
                StatusFSM.DETECTING
                | StatusFSM.FACE_DETECTED_LEVEL_A
                | StatusFSM.FACE_DETECTED_LEVEL_C
                # | StatusFSM.QRCODE_DETECTED TODO: add QRCODE Acts
            ):
                self.passage_start = time.time()
                self._set_status_and_progress(
                    status=StatusFSM.FACE_DETECTED_LEVEL_B,
                )
            case StatusFSM.FACE_DETECTED_LEVEL_B:
                label = self.svm_model.recognize(
                    face_coords=self.detected_face["rect"],  # type: ignore
                    cv_rgb=self.cv_rgb,
                    server=self.server,
                )
                self.labels.append(label)
                date = datetime.fromtimestamp(self.passage_start)  # type: ignore
                self._save_frame(
                    cv_rgb=self.cv_rgb,
                    name=f"{date.isoformat(timespec='seconds')}--{len(self.labels)}",
                )

                if len(self.labels) >= self.MAX_LABELS_COUNT:  # type: ignore
                    print("_server_passage_request")
                    self._server_passage_request()  # TODO: find frequent_label
                else:
                    self._set_status_and_progress(
                        status=StatusFSM.FACE_DETECTED_LEVEL_B,
                        progress=int(
                            len(self.labels)
                            / self.MAX_LABELS_COUNT  # type: ignore
                            * 95
                        ),
                    )

            case StatusFSM.ALLOWED:
                self._stage_check_allowed_status()
            case StatusFSM.NOT_ALLOWED:
                self._stage_check_not_allowed_status()

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
                        / self.detected_face["side"]  # type: ignore
                        * 100
                    ),
                )

            case StatusFSM.FACE_DETECTED_LEVEL_B:
                self._full_reset()
                self._set_status_and_progress(
                    status=StatusFSM.FACE_DETECTED_LEVEL_C,
                    progress=int(
                        self.turnstile_settings.gr_level_c
                        / self.detected_face["side"]  # type: ignore
                        * 100
                    ),
                )
            case StatusFSM.ALLOWED:
                self._stage_check_allowed_status()
            case StatusFSM.NOT_ALLOWED:
                self._stage_check_not_allowed_status()

    def _stage_nothing(self, status):
        # TODO: give turnstile state to server
        match status:
            case StatusFSM.NOT_ACTIVE:
                if turnstile_settings := self.server.turnstile_active():
                    self.svm_model.download(server=self.server)
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
            case (
                StatusFSM.DETECTING
                | StatusFSM.FACE_DETECTED_LEVEL_A
                | StatusFSM.FACE_DETECTED_LEVEL_C
            ):
                self._set_status_and_progress(
                    status=StatusFSM.DETECTING,
                )
            case StatusFSM.QRCODE_DETECTED | StatusFSM.FACE_DETECTED_LEVEL_B:
                self._full_reset()
                self._set_status_and_progress(
                    status=StatusFSM.DETECTING,
                )
            case StatusFSM.ALLOWED:
                self._stage_check_allowed_status()
            case StatusFSM.NOT_ALLOWED:
                self._stage_check_not_allowed_status()

    def _stage_perfomance(self):
        performance_params = dict()
        performance_params["fps"] = self.fps.get_frames_per_second()
        performance_params["brt"] = self.open_cv.get_brightness(frame=self.frame)

        self.open_cv.output_performance(
            frame=self.frame,
            params=performance_params,
            width=self.width,
            height=self.height,
        )

    def _stage_check_allowed_status(self):
        passing_time = time.time() - self.passage_time  # type: ignore

        #######################
        #                     #
        #   TODO: algorithm   #
        #                     #
        #######################

        if passing_time >= self.PASSAGE_TIME_LIMIT:
            self._turnstile_close_gate()
            self._set_status_and_progress(
                status=StatusFSM.DETECTING,
            )
            self.passage_frequent_label = None
        else:
            self._set_status_and_progress(
                status=StatusFSM.ALLOWED,
                progress=int(passing_time / self.PASSAGE_TIME_LIMIT * 100),
            )

    def _stage_check_not_allowed_status(self):
        passing_time = time.time() - self.passage_time  # type: ignore

        #######################
        #                     #
        #   TODO: algorithm   #
        #                     #
        #######################

        if passing_time >= self.PASSAGE_TIME_LIMIT:
            self._set_status_and_progress(
                status=StatusFSM.DETECTING,
            )
            self.passage_frequent_label = None
        else:
            self._set_status_and_progress(
                status=StatusFSM.NOT_ALLOWED,
                progress=int(passing_time / self.PASSAGE_TIME_LIMIT * 100),
            )

    # PASSING ALGORITHM
    def _passing_algorithm(self, passing_time):
        if self.passing_algorithm:
            return self._passing_algorithm_launch(passing_time)
        if self.detected_face is None:
            return
        
        label = self.svm_model.recognize(
            face_coords=self.detected_face["rect"],  # type: ignore
            cv_rgb=self.cv_rgb,
            server=self.server,
        )
        self.labels.append(label)

    def _passing_algorithm_launch(self, passing_time):
        if passing_time < 2:
            return
        if (self.PASSAGE_TIME_LIMIT - passing_time) < 1:
            return
        if self.passing_algorithm_time is None:
            self.passing_algorithm_time = time.time()

        passing_algorithm_time = time.time() - self.passing_algorithm_time
        if passing_algorithm_time > 1:
            self._passing_algorithm_reset()
            frequent_label = self._get_frequent_label()
            self._passing_algorithm_check(frequent_label)
        if self.detected_face is None:
            return

        label = self.svm_model.recognize(
            face_coords=self.detected_face["rect"],  # type: ignore
            cv_rgb=self.cv_rgb,
            server=self.server,
        )
        self.labels.append(label)

    def _passing_algorithm_check(self, frequent_label):
        if self.passage_frequent_label != frequent_label:
            self.passing_algorithm = False

    def _passing_algorithm_reset(self):
        self.labels = []
        self.passing_algorithm_time = None

    # SET_PART
    def _set_data_input(
        self,
        width,
        height,
        frame,
        cv_gray,
        cv_rgb,
        detected_face,
    ):
        # Data Input
        self.width = width
        self.height = height
        self.frame = frame
        self.cv_gray = cv_gray
        self.cv_rgb = cv_rgb
        self.detected_face = detected_face

        # Utils
        self.fps.get_frames_per_second()

    def _set_turnstile_settings_update(self, turnstile_settings_update):
        for name, value in turnstile_settings_update.model_dump(
            exclude_unset=True,
            exclude_none=True,
        ).items():
            self.turnstile_settings = self.turnstile_settings_default
            setattr(self.turnstile_settings, name, value)

    def _set_status_and_progress(self, status, progress=0):
        self.status = status
        self.progress = progress

    # SERVER_PART
    def _server_passage_request(self):

        frequent_label = self._get_frequent_label()
        if frequent_label is None:
            # TODO: if server let down
            print("frequent_label is None")
            self.passage_time = time.time()
            self._set_status_and_progress(
                status=StatusFSM.NOT_ALLOWED,  #  <- There should be an another status
            )
            return

        passage = self.server.turnstile_passage(
            frequent_label=frequent_label,
            svm_model_id=self.svm_model.svm_model_id,
        )

        if passage is None:
            # TODO: if server let down
            print("passage request is None")
            self.passage_time = time.time()
            self._set_status_and_progress(
                status=StatusFSM.NOT_ALLOWED,  #  <- There should be an another status
            )
            return

        self._turnstile_passage_access(passage)
        self.passage_frequent_label = frequent_label

        self.db.set_passage(
            passage_id=passage.id,
            passage_duration=self._turnstile_passage_duration(),
            frequent_label=frequent_label,
        )

    # TURNSTILE_PART
    def _turnstile_passage_access(self, passage):
        self.passing_algorithm = True
        if passage.access:
            self._turstile_open_gate()
            self._set_status_and_progress(
                status=StatusFSM.ALLOWED,
            )
        else:
            self.passage_time = time.time()
            self._set_status_and_progress(
                status=StatusFSM.NOT_ALLOWED,
            )

    def _turnstile_passage_duration(self):
        passage_end = time.time()
        passage_duration = int(self.passage_start - passage_end)  # type: ignore
        return passage_duration

    def _turstile_open_gate(self):
        self.gpio.open_gate()
        self.passage_time = time.time()

    def _turnstile_close_gate(self):
        self.gpio.close_gate()

    # UTILS_PART
    def _utils_set_face_frames_count(self):
        self.passage_start = time.time()

    def _save_frame(self, cv_rgb, name):
        ext, buf = cv.imencode(f"frame{name}.png", cv_rgb)
        if ext:
            bytes_io = io.BytesIO(buf.tobytes())
            file_name = f"{name}.png"
            file_path = BASEDIR.parent / "data" / "passages" / file_name
            with open(f"{file_path}", "wb") as f:
                f.write(bytes_io.getvalue())

    def _get_frequent_label(self):
        collected_labels = self.labels
        self.labels = []

        if len(collected_labels) <= 3:
            return None

        frequent_label = max(set(collected_labels), key=collected_labels.count)
        self.frequent_label = frequent_label
        required_quantity = int(
            self.MAX_LABELS_COUNT * self.FREQUENT_LABEL_PERCENT / 100
        )
        return (
            frequent_label
            if collected_labels.count(frequent_label) >= required_quantity
            else None
        )

    def _full_reset(self):
        duration = self._turnstile_passage_duration()
        if duration > 5:
            self.labels = []
