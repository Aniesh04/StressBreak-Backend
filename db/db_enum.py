import enum
from sqlalchemy import Enum

class RecommendationType(enum.Enum):
    """Enumeration for recommendation types"""
    MUSIC = "music"
    FOOD = "food"
    EXERCISE = "exercise"
    MOVIE = "movie"

class UserRole(enum.Enum):
    """Enumeration for user roles"""
    STUDENT = "student"
    EMPLOYEE = "employee"
    ENTREPRENEUR = "entrepreneur"
    PARENT = "parent"
