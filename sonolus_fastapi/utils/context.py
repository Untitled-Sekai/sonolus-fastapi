from pydantic import BaseModel
from typing import Optional, TypeVar, Generic

T = TypeVar('T')

class SonolusContext(BaseModel, Generic[T]):
    user_session: Optional[str] = None
    request: Optional[T] = None
    is_dev: bool = False