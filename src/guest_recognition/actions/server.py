import requests

from core import settings
from core.schemas import TurnstileSettings, TurnstilePassage


class Server:
    def __init__(self, token):
        self.server_domain = settings.app.server_domain
        self.token = token

    def turnstile_active(self, token):
        if token:
            self.token = token
        try:
            return self._request_turnstile_activating()
        except:
            return None

    def turnstile_passage(self, frames):
        try:
            return self._request_turnstile_passage(frames=frames)
        except:
            return None

    def _request_turnstile_activating(self):
        url = self._create_url(path="api/v1/turnstile/activate")
        headres = self._get_headers_with_token()
        response = requests.patch(
            url=url,
            headres=headres,
        )

        response.raise_for_status()

        turnstile_settings_data = response.json()
        turnstile_settings = TurnstileSettings(**turnstile_settings_data)
        return turnstile_settings

    def _request_turnstile_passage(self, frames):
        url = self._create_url(path="api/v1/turnstile/passage")
        headres = self._get_headers_with_token()
        response = requests.post(url=url, headres=headres, files={"frames": frames})

        response.raise_for_status()

        turnstile_passage_data = response.json()
        turnstile_passage = TurnstilePassage(**turnstile_passage_data)
        return turnstile_passage

    def _create_url(self, path):
        return f"{self.server_domain}/{path}"

    def _get_headers_with_token(self):
        if self.token is None:
            raise Exception("There is no token in for 'x-auth-token' headers")
        return {"x-auth-token": self.token}
