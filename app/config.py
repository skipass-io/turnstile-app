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
    face_detector_settings = FaceDetectorSettings()
    DATA_DIR = f"{BASE_DIR}/app/data"

    haarcascade_file = "haarcascade_frontalface_default.xml"
    haarcascade_path = f"{DATA_DIR}/haarcascades/{haarcascade_file}"

    svm_model_file = "svm_model_160x160.pkl"
    svm_model_path = f"{DATA_DIR}/svm_model/{svm_model_file}"

    embeddings_file = "embeddings.npz"
    embeddings_path = f"{DATA_DIR}/embeddings/{embeddings_file}"
