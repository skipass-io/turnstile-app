from pathlib import Path
import os

# settings for tensorflow logging
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

BASE_DIR = Path(__file__).parent.parent.parent


# App Settings
class AppSettings:
    # TODO: target for vetical screen size 720:1280
    picam2_vertical_size = (595, 1280)
    picam2_horizontal_size = (1280, 595)
    # Font Settings
    font_name = "Poppins-Regular.ttf"
    font_path = f"{BASE_DIR}/app/assets/fonts/{font_name}"


# DB Settings
class DBSQLiteSettings:
    scaffold_sql = f"{BASE_DIR}/app/db/scaffod.sql"
    db_name = "db.sqlite"
    db_path = f"{BASE_DIR}/data/database/{db_name}"


# Guest Recognition Settings
class FaceDetectorSettings:
    scale_factor = 1.1  # 1.3
    min_neighbors = 5
    scalar_detect = 7
    scalar_recognition = 3


class GuestRecognitionColors:
    # MAGENTA
    MAGENTA_HEX = "9400D3"
    MAGENTA_RGB = (148, 0, 211)
    # BLUE
    BLUE_HEX = "34A9ED"
    BLUE_RBG = (52, 169, 237)
    # GREEN
    GREEN_HEX = "22CD69"
    GREEN_RBG = (34, 205, 105)
    # RED
    RED_HEX = "ED451F"
    RED_RBG = (237, 69, 31)


class GuestRecognitionData:
    DATA_DIR = f"{BASE_DIR}/data"

    haarcascade_file = "haarcascade_frontalface_default.xml"
    haarcascade_path = f"{DATA_DIR}/haarcascades/{haarcascade_file}"

    svm_model_file = "svm_model_160x160.pkl"
    svm_model_path = f"{DATA_DIR}/svm_model/{svm_model_file}"

    embeddings_file = "embeddings.npz"
    embeddings_path = f"{DATA_DIR}/embeddings/{embeddings_file}"


class GuestRecognitionSettings:
    face_detector_settings = FaceDetectorSettings()
    colors = GuestRecognitionColors()
    data = GuestRecognitionData()
