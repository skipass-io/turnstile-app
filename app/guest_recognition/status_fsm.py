from enum import Enum


class StatusFSM(Enum):
    """
    Statuses for GuestRecognition (Finite-State Machine)
    ---
    - `NOT_READY`:
    - `GET_READY`:
    - `SEARCHING`:
    - `GET_CLOSER`: 
    - `QRCODE_SCANNING`:
    - `FACE_RECOGNITION`:
    - `ALLOWED`:
    - `NOT_ALLOWED`:
    - `ERROR`:
    """

    NOT_READY = "not_ready"
    GET_READY = "get_ready"
    SEARCHING = "searching"
    GET_CLOSER = "get_closer"
    QRCODE_SCANNING = "qrcode_scanning"
    FACE_RECOGNITION = "face_recognition"
    ALLOWED = "allowed"
    NOT_ALLOWED = "not_allowed"
    ERROR = "error"
