from typing import Any, Optional

class Query:
    """Query object for filtering and searching items."""
    
    def __init__(self, raw: dict[str, Any]) -> None:
        """Initialize Query with raw dictionary.
        
        Args:
            raw: Raw query parameters dictionary
        """
        self.raw: dict[str, Any] = raw