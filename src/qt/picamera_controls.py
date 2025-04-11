from libcamera import controls

from core.config import AeConstraintModeEnum
from core.config import AeExposureModeEnum
from core.config import AeMeteringModeEnum


class PicameraContols:
    def __init__(self):
        self.id = None
        self._picamera_controls = {}

    def is_new_settings(self, turnstile_settings):
        if self.id == turnstile_settings.id:
            return None
        self._picamera_controls = self._create_picamera_controls(turnstile_settings)
        self.id = turnstile_settings.id
        return self._picamera_controls
        

    def get_last_controls(self):
        return self._picamera_controls

    def _create_picamera_controls(self, turnstile_settings):
        return {
            "AeConstraintMode": self._ae_constraint_mode(
                turnstile_settings.ae_constraint_mode
            ),
            "AeEnable": turnstile_settings.ae_enable,
            "AeExposureMode": self._ae_exposure_mode(
                turnstile_settings.ae_exposure_mode
            ),
            "AnalogueGain": turnstile_settings.analogue_gain,
            "AeMeteringMode": self._ae_metering_mode(
                turnstile_settings.ae_metering_mode
            ),
            "Brightness": turnstile_settings.brightness,
            "Contrast": turnstile_settings.contrast,
            "ExposureTime": turnstile_settings.exposure_time,
            "ExposureValue": turnstile_settings.exposure_value,
        }

    def _ae_constraint_mode(self, ae_constraint_mode: AeConstraintModeEnum):
        match ae_constraint_mode:
            case AeConstraintModeEnum.NORMAL:
                return controls.AeConstraintModeEnum.Normal
            case AeConstraintModeEnum.HIGHLIGHT:
                return controls.AeConstraintModeEnum.Highlight
            case AeConstraintModeEnum.SHADOWS:
                return controls.AeConstraintModeEnum.Shadows
            case AeConstraintModeEnum.CUSTOM:
                return controls.AeConstraintModeEnum.Custom

    def _ae_exposure_mode(self, ae_exposure_mode: AeExposureModeEnum):
        match ae_exposure_mode:
            case AeExposureModeEnum.NORMAL:
                return controls.AeExposureModeEnum.Normal
            case AeExposureModeEnum.SHORT:
                return controls.AeExposureModeEnum.Short
            case AeExposureModeEnum.LONG:
                return controls.AeExposureModeEnum.Long
            case AeExposureModeEnum.CUSTOM:
                return controls.AeExposureModeEnum.Custom

    def _ae_metering_mode(self, ae_metering_mode: AeMeteringModeEnum):
        match ae_metering_mode:
            case AeMeteringModeEnum.CENTRE_WEIGHTED:
                return controls.AeMeteringModeEnum.CentreWeighted
            case AeMeteringModeEnum.SPOT:
                return controls.AeMeteringModeEnum.Spot
            case AeMeteringModeEnum.MATRIX:
                return controls.AeMeteringModeEnum.Matrix
            case AeMeteringModeEnum.CUSTOM:
                return controls.AeMeteringModeEnum.Custom
