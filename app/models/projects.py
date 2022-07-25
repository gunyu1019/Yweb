import datetime
import base64
from typing import Any, Dict, List, Optional
from .language import Language
from .category import Category


class Button:
    def __init__(self, name: str, link: str, icon: str):
        self.name: str = name
        self.link: str = link
        self.icon: str = icon


class Project:
    __table_name__ = "projects"

    def __init__(self, payload: Dict[str, Any]):
        self._payload = payload

        self.id: int = payload['id']
        self.title: str = payload['title']
        self.content: Optional[str] = payload.get('content')
        self.icon: bytes = payload.get('icon')
        self.created_at: datetime.datetime = payload.get('created_at')
        self.category: Optional[int] = payload.get('category')
        self.language: Optional[int] = payload.get('language')
        self.github: Optional[str] = payload.get('github')
        self.website: Optional[str] = payload.get('website')
        self.tags: Optional[List[str]] = payload.get('tags')
        self.button: Optional[Button] = None

        button_data = {}
        for key, value in self._payload.items():
            if key.startswith("button_") and value is not None:
                button_data[key.replace('button_', '')] = value
        if {'name', 'icon', 'link'} == set(button_data.keys()):
            self.button = Button(**button_data)

    def contain_language(self, languages: List[Language], value: Optional[List[str]]) -> bool:
        if value is None or len(value) == 0 or value == ['']:
            return True
        key = 0
        for language in languages:
            if language.id_string in value:
                key += language.id
        return key & self.language != 0

    def contain_category(self, categories: List[Category], value: Optional[str]) -> bool:
        if value is None or value == '':
            return True
        for category in categories:
            if category.id_string == value and self.category == category.id:
                return True
        return False

    def s_language(self, languages: List[Language]) -> str:
        key = []
        for language in languages:
            if language.id & self.language != 0:
                key.append(language.name)
        return ", ".join(key)

    def s_category(self, categories: List[Category]) -> str:
        for category in categories:
            if self.category == category.id:
                return category.name
        return "unknown"

    @property
    def icon_convert(self):
        if self.icon is None:
            return
        return base64.b64encode(self.icon).decode('utf8')
