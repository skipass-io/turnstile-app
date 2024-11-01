from enum import Enum


class StatusFSM(Enum):
    """
    Statuses for GuestRecognition (Finite-State Machine)
    ---
    - `NOT_READY`:
    - `GET_READY`:
    - `SEARCHING`:
    - `GET_CLOSER`:
    - `STEP_BACK`:
    - `QRCODE_SCANNING`:
    - `FACE_RECOGNITION`:
    - `ALLOWED`:
    - `NOT_ALLOWED`:
    - `ERROR`:
    """

    NOT_READY = "NOT_READY"
    GET_READY = "GET_READY"
    SEARCHING = "SEARCHING"
    GET_CLOSER = "GET_CLOSER"
    STEP_BACK = "STEP_BACK"
    QRCODE_SCANNING = "QRCODE_SCANNING"
    FACE_RECOGNITION = "FACE_RECOGNITION"
    ALLOWED = "ALLOWED"
    NOT_ALLOWED = "NOT_ALLOWED"
    ERROR = "ERROR"
