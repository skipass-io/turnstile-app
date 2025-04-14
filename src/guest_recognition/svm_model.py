import pickle
from typing import Optional

import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC

from core.config import BASEDIR
from guest_recognition.actions import DB, Server
from guest_recognition.embedder import Embedder


DATA_DIR = BASEDIR.parent.resolve() / "data"
SVM_MODELS_DIR = DATA_DIR / "svm_models"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"


class SVMModel:
    def __init__(self) -> None:
        # Actions
        self.db = DB()

        # Main
        self.svm_model_id: Optional[int] = self.db.get_svm_model_id()
        self.svm_model: Optional[SVC] = None
        self.encoder: Optional[LabelEncoder] = None
        self.embedder = Embedder()

    def recognize(self, face_coords, cv_rgb, server) -> str:
        self._check_svm_model_and_encoder_loaded(server)
        ypred = self.embedder.get_embeddings(
            face_coords=face_coords,
            cv_rgb=cv_rgb,
        )
        y_pred = self.svm_model.predict(ypred)
        label: str = self.encoder.inverse_transform(y_pred)[0]
        return label

    def load(self, svm_model_id: int) -> None:
        encoder = LabelEncoder()
        with open(self._svm_model_path(svm_model_id), "rb") as f:
            self.svm_model = pickle.loads(f.read())
        with open(self._embeddings_path(svm_model_id), "rb") as f:
            faces_embeddings = np.load(f.read())
            Y = faces_embeddings["arr_1"]
            self.encoder = encoder.fit(Y)

        self.svm_model_id = svm_model_id

    def download(self, server: Server):  # TODO: WITH INIT ACTIVATE TOKEN
        svm_model_id = server.turnstile_last_svm_model_id()
        if self.svm_model_id == svm_model_id:
            return False
        svm_model_downloaded = server.download_svm_model(
            save_path=self._svm_model_path(svm_model_id)
        )
        embeddings_downloaded = server.download_embeddings(
            save_path=self._embeddings_path(svm_model_id)
        )
        if svm_model_downloaded and embeddings_downloaded:
            self.svm_model_id = svm_model_id
            self.db.set_svm_model_id(svm_model_id)
            self.load(svm_model_id)
            return True
        return False

    def _check_svm_model_and_encoder_loaded(self, server: Server):
        if self.svm_model_id is None:
            self.download(server)
        if self.svm_model is None or self.encoder is None:
            self.load(self.svm_model_id)  # type: ignore

    def _svm_model_path(self, svm_model_id):
        return f"{SVM_MODELS_DIR}/svm_model_{svm_model_id}.pkl"

    def _embeddings_path(self, svm_model_id):
        return f"{EMBEDDINGS_DIR}/embeddings_{svm_model_id}.npz"
