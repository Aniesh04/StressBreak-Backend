from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, timedelta

from db.database import get_db

# Create router with prefix and tags defined here
router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)

