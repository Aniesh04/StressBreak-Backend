from sqlalchemy import Boolean, Column, Integer, DateTime
from sqlalchemy.sql import func
from .database import Base


class BasicModel(Base):
    """Basic Model Abstract Class"""

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True) 