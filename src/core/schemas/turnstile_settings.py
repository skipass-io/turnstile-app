from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from core.config import AeConstraintModeEnum, AeExposureModeEnum, AeMeteringModeEnum


class TurnstileSettings(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    turnstile_id: int
    show_performance: bool
    gr_level_a: int
    gr_level_b: int
    gr_level_c: int
    update_interval: int
    camera_environment_state_id: Optional[int]
    ae_constraint_mode: Optional[AeConstraintModeEnum]
    ae_enable: Optional[bool]
    ae_exposure_mode: Optional[AeExposureModeEnum]
    analogue_gain: Optional[float]
    ae_metering_mode: Optional[AeMeteringModeEnum]
    brightness: Optional[float]
    contrast: Optional[float]
    exposure_time: Optional[int]
    exposure_value: Optional[float]
