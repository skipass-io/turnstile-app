from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


# COLORS
MAGENTA_HEX = "9400D3"
MAGENTA_RGB = (148, 0, 211)
LIGHT_BLUE_HEX = "ADDBF6"
LIGHT_BLUE_RGB = (202, 80, 82)
BLUE_HEX = "34A9ED"
BLUE_RBG = (52, 169, 237)
GREEN_HEX = "22CD69"
GREEN_RBG = (34, 205, 105)
RED_HEX = "ED451F"
RED_RBG = (237, 69, 31)


# ./src - basedir
BASEDIR = Path(__file__).parent.parent.resolve()
DONTENV_TEMPLATE = BASEDIR / ".env.template"
DONTENV = BASEDIR / ".env"


class AeConstraintModeEnum(str, Enum):
    NORMAL = "Normal"
    HIGHLIGHT = "Highlight"
    SHADOWS = "Shadows"
    CUSTOM = "Custom"


class AeExposureModeEnum(str, Enum):
    NORMAL = "Normal"
    SHORT = "Short"
    LONG = "Long"
    CUSTOM = "Custom"


class AeMeteringModeEnum(str, Enum):
    CENTRE_WEIGHTED = "CentreWeighted"
    SPOT = "Spot"
    MATRIX = "Matrix"
    CUSTOM = "Custom"


class AppConfig(BaseModel):
    server_domain: str
    recruitment_form_url: str


class QTConfig(BaseModel):
    font_name: str = "Poppins-SemiBold.ttf"
    font_path: Path = BASEDIR / "assets" / "fonts" / font_name


class GPIOConfig(BaseModel):
    pin_gate: str


class TurnstileDefaultConfig(BaseModel):
    id: int = 0
    created_at: datetime = datetime.now()
    turnstile_id: int = 0
    show_performance: bool
    gr_level_a: int
    gr_level_b: int
    gr_level_c: int
    update_interval: int
    camera_environment_state_id: Optional[int] = None
    ae_constraint_mode: AeConstraintModeEnum = AeConstraintModeEnum.NORMAL
    ae_enable: bool
    ae_exposure_mode: AeExposureModeEnum = AeExposureModeEnum.NORMAL
    analogue_gain: float
    ae_metering_mode: AeMeteringModeEnum = AeMeteringModeEnum.CENTRE_WEIGHTED
    brightness: float
    contrast: float
    exposure_time: int
    exposure_value: float


class TurnstileConfig(BaseModel):
    gpio: GPIOConfig
    default: TurnstileDefaultConfig

    passage_time_limit: int

    # Settigs


class DatabaseConfig(BaseModel):
    db_name: str = "db.sqlite"
    path: Path = BASEDIR.parent / "data" / "database" / db_name
    scaffold_sql: Path = BASEDIR / "core" / "scaffold.sql"


class FaceDetectorConfig(BaseModel):
    haarcascade_file: str = "haarcascade_frontalface_default.xml"
    haarcascade_path: Path = BASEDIR / "assets" / "models" / haarcascade_file
    scale_factor: float = 1.1
    min_neighbors: int = 5
    scalar_detect: int = 7
    scalar_recognition: int = 3


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(DONTENV_TEMPLATE, DONTENV),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    app: AppConfig
    qt: QTConfig = QTConfig()
    turnstile: TurnstileConfig
    db: DatabaseConfig = DatabaseConfig()
    fd: FaceDetectorConfig = FaceDetectorConfig()


settings = Settings()
