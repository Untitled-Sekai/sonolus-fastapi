from pydantic import BaseModel, Field, create_model
from typing import Optional, Type, List
from sonolus_models import ServerForm

def option_to_python_type(opt):
    """ServerOptionの型に基づいて適切なPython型を返す"""
    if opt.type == "text":
        return str
    elif opt.type == "textArea":
        return str
    elif opt.type == "slider":
        return float
    elif opt.type == "toggle":
        return bool
    elif opt.type == "select":
        return str
    elif opt.type == "multi":
        return str  # カンマ区切りの文字列として受信される
    elif opt.type == "serverItem":
        return str  # Optional[str]だが、基本型はstr
    elif opt.type == "serverItems":
        return List[str]  # List[str]型
    elif opt.type == "collectionItem":
        return str  # 通常はstring型として扱う
    elif opt.type == "file":
        return str
    else:
        # 未知の型の場合はstrをデフォルトとする
        return str

def create_query_model(name: str, form: ServerForm) -> Type[BaseModel]:
    fields = {}

    for opt in form.options:
        py_type = option_to_python_type(opt)
        if not opt.required:
            py_type = Optional[py_type]

        # def_フィールドの値を正しく取得
        # Pydanticのaliasに対応するため、直接アクセスする
        default = opt.def_

        fields[opt.query] = (
            py_type,
            Field(default=default, description=str(opt.name)),
        )

    return create_model(name, **fields)
