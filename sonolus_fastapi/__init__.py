"""
Sonolus FastAPI - FastAPI wrapper for Sonolus server creation and management
"""

__version__ = "0.5.9.6"
__author__ = "pim4n"

from .index import Sonolus, SonolusSpa

__all__ = ['Sonolus', 'SonolusSpa' ]