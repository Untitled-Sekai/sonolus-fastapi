from pydantic import BaseModel
from typing import Optional, TypeVar, Generic, Dict, Union
from ..model.ServerOption import ServerOption

T = TypeVar('T')

# サーバーオプションの値として想定される型
OptionValue = Union[str, int, float, bool]

class SonolusContext(BaseModel, Generic[T]):
    user_session: Optional[str] = None
    request: Optional[T] = None
    localization: Optional[str] = None
    options: Optional[Dict[str, OptionValue]] = None
    is_dev: bool = False