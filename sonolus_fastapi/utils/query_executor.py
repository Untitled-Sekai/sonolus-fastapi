from typing import Any, TypeVar
from .query import Query

T = TypeVar('T')

def apply_query(items: list[Any], query: Query) -> list[Any]:
    """Apply query filters to items list.
    
    Args:
        items: List of items to filter
        query: Query object containing filter parameters
        
    Returns:
        Filtered list of items
    """
    if hasattr(query, "keywords") and query.keywords:
        items = [
            i for i in items
            if query.keywords.lower() in i.title.lower()
        ]
    return items

def paginate(items: list[T], page: int = 1, page_size: int = 20) -> list[T]:
    """Paginate a list of items.
    
    Args:
        items: List of items to paginate
        page: Page number (1-based)
        page_size: Number of items per page
        
    Returns:
        Paginated list of items
    """
    start = (page - 1) * page_size
    end = start + page_size
    return items[start:end]