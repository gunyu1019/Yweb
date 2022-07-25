from typing import Any, Dict, Optional


class Language:
    __table_name__ = "language"

    def __init__(
            self, payload: Dict[str, Any]
    ):
        self.id: int = payload['id']
        self.id_string: str = payload['id_string']
        self.name: str = payload['name']
        self.icon: Optional[bytes] = payload.get('icon')

    def contain(self, value: id):
        return self.id & value != 0
