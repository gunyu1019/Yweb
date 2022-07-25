from urllib.parse import urlencode
from urllib.request import Request
from urllib.request import urlopen
from typing import List, Tuple

from .model import AccessToken, User
from .utils import from_json, Pointer

BASE = "https://login.microsoftonline.com"


class Microsoft(Pointer):
    def __init__(
            self,
            client_id: str,
            client_secret: str
    ):
        super().__init__()
        self.client_id = client_id
        self.client_secret = client_secret

    def add_parameter(
            self,
            position: int,
            key: str,
            value: str,
            ended: bool = False
    ) -> None:
        self._pointer_value[position] += f"{key}={value}"
        if not ended:
            self._pointer_value[position] += "&"

    def authorize(
            self,
            redirect_uri: str,
            scope: List[str],
            tenant: str = "common",
            response_type: str = "code",
            response_mode: str = "query"
    ) -> str:
        _scope = "%20".join(scope)
        _url = BASE + "/" + tenant + "/oauth2/v2.0/authorize?"
        position = self._add_pointer(_url)

        self.add_parameter(position, "client_id", self.client_id)
        self.add_parameter(position, "redirect_uri", redirect_uri)
        self.add_parameter(position, "response_type", response_type)
        self.add_parameter(position, "scope", _scope)
        self.add_parameter(position, "response_mode", response_mode, ended=True)
        return self._get_pointer(position)

    def token(
            self,
            redirect_uri: str,
            scope: List[str],
            code: str,
            tenant: str = "common",
            grant_type: str = "authorization_code"
    ) -> Tuple[str, dict]:
        _scope = " ".join(scope)
        return BASE + "/" + tenant + "/oauth2/v2.0/token", {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": redirect_uri,
            "code": code,
            "scope": _scope,
            "grant_type": grant_type
        }

    def generate_access_token(
            self,
            scope: List[str],
            redirect_uri: str,
            code: str
    ):
        url, data = self.token(code=code, redirect_uri=redirect_uri, scope=scope)
        request = Request(
            url=url,
            data=urlencode(data).encode(),
            headers={
                "Accept": "application/x-www-form-urlencoded",
                "User-Agent": "yhs.kr (Microsoft OAuth)"
            },
            method="POST"
        )

        response = urlopen(request)
        result = from_json(response.read().decode())
        return AccessToken.from_payload(result)

    @staticmethod
    def get_user(access_token: AccessToken) -> User:
        request = Request(
            url="https://graph.microsoft.com/v1.0/me",
            headers={
                "Accept": "application/json",
                "Authorization": f"{access_token.type} {access_token.token}",
                "User-Agent": "yhs.kr (Microsoft OAuth)"
            }
        )

        response = urlopen(request)
        result = from_json(response.read().decode())
        return User(result)
