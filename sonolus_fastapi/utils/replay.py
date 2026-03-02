"""ReplayItem processing utilities"""
from typing import Any, Dict, Optional
from pydantic import BaseModel


def normalize_descriptions(data: Any) -> Any:
    """
    Recursively normalize description fields from None to empty string.
    
    This is needed because Sonolus expects empty strings for description fields,
    but the client may send None values or omit the field entirely.
    
    Args:
        data: The data to normalize (dict, BaseModel, or primitive type)
        
    Returns:
        The normalized data with description fields converted from None to ""
    """
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if key == "description":
                # Set to empty string if None or missing
                result[key] = "" if value is None else value
            elif isinstance(value, (dict, BaseModel)):
                result[key] = normalize_descriptions(value)
            elif isinstance(value, list):
                result[key] = [normalize_descriptions(item) for item in value]
            else:
                result[key] = value
        
        # Add description field if it doesn't exist
        if "description" not in result:
            result["description"] = ""
        
        return result
    elif isinstance(data, BaseModel):
        # Convert to dict, normalize, then reconstruct
        data_dict = data.model_dump(mode='python')
        normalized = normalize_descriptions(data_dict)
        return type(data).model_validate(normalized)
    elif isinstance(data, list):
        return [normalize_descriptions(item) for item in data]
    else:
        return data


def normalize_replay_item(replay_data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Normalize a replay item's description fields.
    
    This function ensures all description fields in a ReplayItem (and nested items
    like LevelItem, EngineItem, etc.) are set to empty strings instead of None.
    
    Args:
        replay_data: The replay item data as a dictionary
        
    Returns:
        The normalized replay item data, or None if input was None
    """
    if replay_data is None:
        return None
    
    return normalize_descriptions(replay_data)
