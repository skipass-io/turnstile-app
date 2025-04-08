from enum import Enum


class StatusFSM(Enum):
    """
    Statuses for GuestRecognition (Finite-State Machine)
    ---
    - `NOT_ACTIVE`: Not token in app
    - `DETECTING`: Detecting a QR code or a face in the frame
    - `QRCODE_DETECTED`: QR-Code detected in the frame
    - `FACE_DETECTED_LEVEL_A`: Face detected far away in the frame
    - `FACE_DETECTED_LEVEL_B`: Face detected at Turnstile in the frame
    - `FACE_DETECTED_LEVEL_C`: Face detected very close in the frame
    - `ALLOWED`: Turnstile opens the gate after Guest Recognition
    - `NOT_ALLOWED`: Turnstile keeps the gate closed after Guest Recognition
    """
    NOT_ACTIVE = "NOT_ACTIVE"
    DETECTING = "DETECTING"
    QRCODE_DETECTED = "QRCODE_DETECTED"
    FACE_DETECTED_LEVEL_A = "FACE_DETECTED_LEVEL_A"
    FACE_DETECTED_LEVEL_B = "FACE_DETECTED_LEVEL_B"
    FACE_DETECTED_LEVEL_C = "FACE_DETECTED_LEVEL_C"
    ALLOWED = "ALLOWED"
    NOT_ALLOWED = "NOT_ALLOWED"
