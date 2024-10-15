"""qt app customs exceptions"""


class NotCorrectStatusGR(Exception):
    """Raise if NotCorrectStatusGR"""

    def __init__(self, current_status, correct_status):
        message = f"Current status: {current_status}; Expected: {correct_status}"
        super().__init__(message)
