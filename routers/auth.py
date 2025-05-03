from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import User # Import User model
from utils.security import get_current_user # Import the dependency

# Create router with prefix and tags defined here
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)
