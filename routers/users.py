from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.database import get_db

# Create router with prefix and tags defined here
router = APIRouter(
    prefix="/users",
    tags=["Users"]
)
