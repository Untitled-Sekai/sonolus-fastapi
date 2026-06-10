"""
Sonolus FastAPI - FastAPI wrapper for Sonolus server creation and management
"""

__version__ = "0.5.10.3"
__author__ = "pim4n"

from .utils.taggable_pydantic import install_sonolus_models_taggable_support

install_sonolus_models_taggable_support()

from .index import Sonolus, SonolusSpa

__all__ = ["Sonolus", "SonolusSpa"]
