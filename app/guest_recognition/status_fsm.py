from enum import Enum


class StatusFSM(Enum):
    """
    Statuses for GuestRecognition (Finite-State Machine)
    ---
    - `GET_READY`:
    - `NOT_READY`:
    - `ERROR`:
    - `SEARCHING`:
    - `PROCESSING`:
    - `ALLOWED`:
    - `NOT_ALLOWED`:
    """

    GET_READY = "get_ready"
    NOT_READY = "not_ready"
    ERROR = "error"
    SEARCHING = "searching"
    PROCESSING = "processing"
    ALLOWED = "allowed"
    NOT_ALLOWED = "not_allowed"
