from datetime import datetime
from typing import Union, List, Dict, Any


class DictObject:
    def __init__(self, payload: Dict[str, Any]):
        self.payload = payload

    def __hasattr__(self, item) -> bool:
        return item in self.payload

    def __getattr__(self, item):
        return self.payload[item]

    def __dict__(self):
        return self.payload


class AccessToken:
    def __init__(
            self,
            access_token: str,
            token_type: str,
            expires_in: int,
            scope: str,
            refresh_token: str = None,
            id_token: str = None,
            **_
    ):
        self.scope = scope.split()
        self.token = access_token
        self.type = token_type
        self.expires = expires_in
        self.refresh_token = refresh_token
        self.id_token = id_token

    @classmethod
    def from_payload(cls, payload: dict):
        if 'token_type' not in payload:
            payload['token_type'] = "Bearer"
        if 'expires_in' not in payload:
            payload['expires_in'] = 0
        if 'scope' not in payload:
            payload['scope'] = ''
        return cls(**payload)

    def to_dict(self) -> dict:
        result = {
            "access_token": self.token,
            "token_type": self.type,
            "scope": " ".join(self.scope),
            "expires_in": self.expires
        }
        if self.refresh_token is not None:
            result['refresh_token'] = self.refresh_token
        if self.id_token is not None:
            result['id_token'] = self.id_token
        return result


class User(DictObject):
    def __init__(self, payload: Dict[str, Any]):
        super(User, self).__init__(payload)
        self.id = payload['id']
