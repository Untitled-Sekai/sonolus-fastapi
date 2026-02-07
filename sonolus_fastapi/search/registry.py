from dataclasses import dataclass
from typing import Optional, Dict, Type
from pydantic import BaseModel
from sonolus_models import ServerForm
from .query_model import create_query_model

@dataclass
class SearchRegistry:
    post: Optional[ServerForm] = None
    playlist: Optional[ServerForm] = None
    level: Optional[ServerForm] = None
    skin: Optional[ServerForm] = None
    background: Optional[ServerForm] = None
    effect: Optional[ServerForm] = None
    particle: Optional[ServerForm] = None
    engine: Optional[ServerForm] = None
    replay: Optional[ServerForm] = None

    _models: Dict[str, Type[BaseModel]] = None

    def __post_init__(self):
        self._models = {}

    def get_form(self, key: str) -> Optional[ServerForm]:
        return getattr(self, key, None)

    def get_query_model(self, key: str) -> Optional[Type[BaseModel]]:
        if key in self._models:
            return self._models[key]

        form = self.get_form(key)
        if form is None:
            return None

        model = create_query_model(f"{key.capitalize()}SearchQuery", form)
        self._models[key] = model
        return model
