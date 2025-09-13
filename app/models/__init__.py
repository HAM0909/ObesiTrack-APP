# app/models/__init__.py
from .base import Base
from .user import User
from .prediction import Prediction  # if you have it

__all__ = ['Base', 'User', 'Prediction']