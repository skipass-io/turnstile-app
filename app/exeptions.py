"""qt app customs exeptions"""

class NotCorrectStatusGR(Exception):
    def __init__(self, message):
        """Raise if NotCorrectStatusGR"""
        # Call the base class constructor with the parameters it needs
        super().__init__(message)