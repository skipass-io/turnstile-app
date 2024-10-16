"""qt app customs exceptions"""


# Guest Recognition
class NotCorrectFrameSizeGR(Exception):
    """Raise if not correct picamera frame size"""

    def __init__(self, frame_size):
        message = f"Need correct frame size (width, height), but got: {frame_size}"
        super().__init__(message)


class NotCorrectStatusGR(Exception):
    """Raise if not correct status FSM"""

    def __init__(self, current_status, correct_statuses):
        message = f"Current status: {current_status}; Expected statuses: {correct_statuses}"
        super().__init__(message)
