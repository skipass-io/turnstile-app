import time
import requests
import json

from core import settings
from core.schemas import TurnstileSettings, TurnstilePassage


class Server:
    def __init__(self, token):
        self.server_domain = settings.app.server_domain
        self.token = token

    def turnstile_active(self, token=None):
        if token:
            self.token = token
        try:
            return self._request_turnstile_activating()
        except Exception as e:
            print("Exception turnstile_active", e)
            time.sleep(settings.app.second_limit_activation_request)
            return None

    def turnstile_passage(self, frequent_label, svm_model_id):
        try:
            return self._request_turnstile_passage(
                frequent_label=frequent_label,
                svm_model_id=svm_model_id,
            )
        except Exception as e:
            print("Exception turnstile_passage", e)
            return None

    def turnstile_last_svm_model_id(self):
        return self._request_turnstile_last_svm_model_id()

    def download_svm_model(self, save_path):
        try:
            url = self._create_url(path="api/v1/turnstile/download_svm_model")
            headers = self._get_headers_with_token()
            response = requests.get(url=url, headers=headers, stream=True)

            response.raise_for_status()

            with open(save_path, "wb") as file:
                file.write(response.content)

            print(f"SVM model successfully downloaded to {save_path}")
            return True
        except Exception as e:
            print(f"Error downloading SVM model: {e}")
            return False

    def download_embeddings(self, save_path):
        try:
            url = self._create_url(path="api/v1/turnstile/download_embeddings")
            headers = self._get_headers_with_token()
            response = requests.get(url=url, headers=headers, stream=True)

            response.raise_for_status()

            with open(save_path, "wb") as file:
                file.write(response.content)

            print(f"Embeddings successfully downloaded to {save_path}")
            return True
        except Exception as e:
            print(f"Error downloading embeddings: {e}")
            return False

    def _request_turnstile_activating(self):
        url = self._create_url(path="api/v1/turnstile/activate")
        headers = self._get_headers_with_token()
        response = requests.patch(
            url=url,
            headers=headers,
        )

        response.raise_for_status()

        turnstile_settings_data = response.json()
        turnstile_settings = TurnstileSettings(**turnstile_settings_data)
        return turnstile_settings

    def _request_turnstile_passage(self, frequent_label, svm_model_id):
        url = self._create_url(path="api/v1/turnstile/passage_label")
        headers = self._get_headers_with_token()
        headers["Content-Type"] = "application/json"
        payload = {"frequent_label": frequent_label, "svm_model_id": svm_model_id}
        response = requests.post(
            url=url,
            headers=headers,
            data=json.dumps(payload),
        )

        response.raise_for_status()

        turnstile_passage_data = response.json()
        turnstile_passage = TurnstilePassage(**turnstile_passage_data)
        return turnstile_passage

    def _request_turnstile_last_svm_model_id(self):
        url = self._create_url(path="api/v1/turnstile/last_svm_model_id")
        headers = self._get_headers_with_token()
        response = requests.post(
            url=url,
            headers=headers,
        )

        response.raise_for_status()

        svm_model_id_data = response.json()
        svm_model_id: int = svm_model_id_data.get("svm_model_id")
        return svm_model_id

    def _create_url(self, path):
        return f"{self.server_domain}/{path}"

    def _get_headers_with_token(self):
        if self.token is None:
            raise Exception("There is no token in for 'x-auth-token' headers")
        return {"x-auth-token": self.token}
