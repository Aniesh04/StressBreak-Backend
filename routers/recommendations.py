from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from db.database import get_db
from db.db_enum import RecommendationType

# Create router with prefix and tags defined here
router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"]
)
