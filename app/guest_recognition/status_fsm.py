from enum import Enum


class StatusFSM(Enum):
    """
    Statuses for GuestRecognition (Finite-State Machine)
    ---
    - `GET_READY`:
    - `NOT_READY`:
    - `ERROR`:
    - `SEARCHING`:
    - `QRCODE_SCANNING`:
    - `FACE_RECOGNITION`:
    - `ALLOWED`:
    - `NOT_ALLOWED`:
    """

    GET_READY = "get_ready"
    NOT_READY = "not_ready"
    ERROR = "error"
    SEARCHING = "searching"
    QRCODE_SCANNING = "qrcode_scanning"
    FACE_RECOGNITION = "face_recognition"
    ALLOWED = "allowed"
    NOT_ALLOWED = "not_allowed"
