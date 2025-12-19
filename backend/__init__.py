"""Backend package initialization"""
from .config import settings
from .main import app

__version__ = "1.0.0"
__all__ = ["app", "settings"]
