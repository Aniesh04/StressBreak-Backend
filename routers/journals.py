from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import User
from .utils import generate_analyze_journal
from utils.security import get_current_user


router = APIRouter(
    prefix="/journals",
    tags=["Journals"]
)

@router.post("/analyze", status_code=status.HTTP_200_OK)
async def analyze_journal_entry(
    entry: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    
    if not entry:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Entry cannot be empty")
    
    analysis_result = generate_analyze_journal(entry)
    
    return analysis_result