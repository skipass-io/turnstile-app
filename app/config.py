from pathlib import Path
import os

# settings for tensorflow logging
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

BASE_DIR = Path(__file__).parent


class GuestRecognitionSettings:
    haarcascade_file = "haarcascade_frontalface_default.xml"
    haarcascade_path = f"{BASE_DIR}/app/data/haarcascades/{haarcascade_file}"


class DBSQLiteSettings:
    scaffold_sql = f"{BASE_DIR}/app/scaffod.sql"
    db_name = "db.sqlite"
    db_path = f"{BASE_DIR}/db/{db_name}"
