from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

# ./src - basedir
BASEDIR = Path(__file__).parent.parent.resolve()
DONTENV_TEMPLATE = BASEDIR / ".env.template"
DONTENV = BASEDIR / ".env"


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


class AppConfig(BaseModel):
    font_name: str = "Poppins-SemiBold.ttf"
    font_path: Path = BASEDIR / "assets" / "fonts" / font_name


class DatabaseConfig(BaseModel):
    db_name: str = "db.sqlite"
    db_path: Path = BASEDIR.parent / "data" / "database" / db_name
    scaffold_sql: Path = BASEDIR / "db" / "scaffold.sql"


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
    app: AppConfig = AppConfig()
    db: DatabaseConfig = DatabaseConfig()
    fd: FaceDetectorConfig = FaceDetectorConfig()

settings = Settings()