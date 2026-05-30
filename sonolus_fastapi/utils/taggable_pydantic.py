"""
Pydantic integration for transparent TaggableItem handling.
"""

from typing import Any

from pydantic import BaseModel
from pydantic_core import core_schema

from sonolus_fastapi.utils.taggable_item import TaggableItem


def unwrap_taggable_items(value: Any) -> Any:
    """
    Recursively unwrap TaggableItem instances in common validation inputs.
    """
    if isinstance(value, TaggableItem):
        return unwrap_taggable_items(object.__getattribute__(value, "_item"))

    if isinstance(value, list):
        return [unwrap_taggable_items(item) for item in value]

    if isinstance(value, tuple):
        return tuple(unwrap_taggable_items(item) for item in value)

    if isinstance(value, dict):
        return {key: unwrap_taggable_items(item) for key, item in value.items()}

    return value


@classmethod
def _taggable_model_core_schema(
    cls: type[BaseModel], source_type: Any, handler: Any
) -> core_schema.CoreSchema:
    schema = handler(source_type)
    return core_schema.no_info_before_validator_function(unwrap_taggable_items, schema)


def install_sonolus_models_taggable_support() -> None:
    """
    Add TaggableItem pre-validation support to sonolus-models classes.

    sonolus-models defines its sections and item references as plain Pydantic
    models, so fields like list[LevelItem] do not see TaggableItem's own schema.
    This wraps each exported sonolus_models BaseModel schema with a lightweight
    pre-validator and rebuilds the models that have already been imported.
    """
    try:
        import sonolus_models
    except ImportError:
        return

    patched_classes: list[type[BaseModel]] = []

    for name in dir(sonolus_models):
        candidate = getattr(sonolus_models, name)
        if not isinstance(candidate, type):
            continue
        if not issubclass(candidate, BaseModel):
            continue
        if candidate.__dict__.get("__sonolus_fastapi_taggable_support__", False):
            continue

        candidate.__get_pydantic_core_schema__ = _taggable_model_core_schema
        candidate.__sonolus_fastapi_taggable_support__ = True
        patched_classes.append(candidate)

    for model_cls in patched_classes:
        try:
            model_cls.model_rebuild(force=True)
        except Exception:
            # Some optional or generic models may depend on names outside their
            # local rebuild namespace. They will still use the patch when their
            # schema is generated later.
            pass


__all__ = ["install_sonolus_models_taggable_support", "unwrap_taggable_items"]
