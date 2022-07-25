from typing import Any, Dict, Optional


class Category:
    __table_name__ = "category"

    def __init__(
            self, payload: Dict[str, Any]
    ):
        self.id: int = payload['id']
        self.id_string: str = payload['id_string']
        self.name: str = payload['name']
        self.icon: Optional[bytes] = payload.get('icon')
