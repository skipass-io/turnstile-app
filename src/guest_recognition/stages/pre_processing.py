import cv2 as cv


class PreProcessing:
    def __init__(self):
        # Pre Processing Data
        self.frame = None
        self.cv_rgb = None
        self.cv_gray = None

    def stage(self, mapped_array):
        self.frame = mapped_array.array
        self.cv_rgb = cv.cvtColor(self.frame, cv.COLOR_BGR2RGB)
        self.cv_gray = cv.cvtColor(self.frame, cv.COLOR_BGR2GRAY)
