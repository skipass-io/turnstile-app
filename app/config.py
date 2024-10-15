from pathlib import Path
import os

# settings for tensorflow logging
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

BASE_DIR = Path(__file__).parent.parent


# DB Settings
class DBSQLiteSettings:
    scaffold_sql = f"{BASE_DIR}/app/scaffod.sql"
    db_name = "db.sqlite"
    db_path = f"{BASE_DIR}/db/{db_name}"


# Guest Recognition Settings
class FaceDetectorSettings:
    scale_factor = 1.3
    min_neighbors = 5
    scalar_face_detect = 7


class GuestRecognitionSettings:
    haarcascade_file = "haarcascade_frontalface_default.xml"
    haarcascade_path = f"{BASE_DIR}/app/data/haarcascades/{haarcascade_file}"
    face_detector_settings = FaceDetectorSettings()
