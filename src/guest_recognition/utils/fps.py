import time


class FPS:
    def __init__(self):
        self.fps = 0
        self.fps_count = 0
        self.start_fps_time = time.time()

    def get_frames_per_second(self):
        self.fps_count += 1
        elapsed_time = time.time() - self.start_fps_time

        if elapsed_time >= 1.0:
            self.fps = self.fps_count / elapsed_time
            self._reset()

        return round(self.fps, 2)
    
    def _reset(self):
        self.fps_count = 0
        self.start_fps_time = time.time()
