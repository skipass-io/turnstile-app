from guest_recognition.status_fsm import StatusFSM
from guest_recognition.stages import PreProcessing, Processing, PostProcessing


class GuestRecognition:
    def __init__(self, frame_size):
        # init data
        self.width = frame_size[0]
        self.height = frame_size[1]

        # status data
        self.status = StatusFSM.NOT_ACTIVE
        self.progress = 0
        self.turnstile_settings = None

        # stages
        self.pre_processing = PreProcessing()
        self.processing = Processing()
        self.post_processing = PostProcessing()

    def run(self, mapped_array):
        self.pre_processing.stage(
            mapped_array=mapped_array,
        )

        self.processing.stage(
            status=self.status,
            frame=self.pre_processing.frame,
            cv_gray=self.pre_processing.cv_gray,
        )

        self.post_processing.stage(
            status=self.status,
            width=self.width,
            height=self.height,
            frame=self.pre_processing.frame,
            cv_rgb=self.pre_processing.cv_rgb,
            cv_gray=self.pre_processing.cv_gray,
            detected_qrcode=self.processing.detected_qrcode,
            detected_face=self.processing.detected_face,
        )

        self.status = self.post_processing.status
        self.progress = self.post_processing.progress
        self.turnstile_settings = self.post_processing.turnstile_settings
