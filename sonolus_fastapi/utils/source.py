from __future__ import annotations

from typing import Any

from pydantic import BaseModel


def strip_source_fields(value: Any) -> Any:
    """`source` フィールドを再帰的に除去したコピーを返す。"""
    if isinstance(value, BaseModel):
        return value.__class__.model_validate(_strip_source_fields_from_python(value.model_dump(mode="python")))
    return _strip_source_fields_from_python(value)



def override_source_fields(value: Any, source: str | None) -> Any:
    """`source` フィールドを再帰的に上書きしたコピーを返す。"""
    if source is None:
        return value

    if isinstance(value, BaseModel):
        return value.__class__.model_validate(_override_source_fields_on_python(value.model_dump(mode="python"), source))
    return _override_source_fields_on_python(value, source)



def _strip_source_fields_from_python(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _strip_source_fields_from_python(item)
            for key, item in value.items()
            if key != "source"
        }
    if isinstance(value, list):
        return [_strip_source_fields_from_python(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_strip_source_fields_from_python(item) for item in value)
    return value



def _override_source_fields_on_python(value: Any, source: str) -> Any:
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if key == "source":
                result[key] = source
            else:
                result[key] = _override_source_fields_on_python(item, source)
        return result
    if isinstance(value, list):
        return [_override_source_fields_on_python(item, source) for item in value]
    if isinstance(value, tuple):
        return tuple(_override_source_fields_on_python(item, source) for item in value)
    return value
