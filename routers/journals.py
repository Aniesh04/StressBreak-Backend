from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import User, Journal
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
    # current_user: User = Depends(get_current_user)
):
    
    if not entry:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Entry cannot be empty")
    
    analysis_result = generate_analyze_journal(entry)
    
    # Save the analysis result to the database
    db.add(Journal(
        user_id=current_user.id,
        journal_content=entry,
        positive_score=analysis_result['sentiment']['positive'],
        negative_score=analysis_result['sentiment']['negative'],
        neutral_score=analysis_result['sentiment']['neutral'],
        happiness_score=analysis_result['emotion']['happiness'],
        sadness_score=analysis_result['emotion']['sadness'],
        fear_score=analysis_result['emotion']['fear'],
        anger_score=analysis_result['emotion']['anger'],
        surprise_score=analysis_result['emotion']['surprise'],
        joy_score=analysis_result['emotion']['joy'],
        love_score=analysis_result['emotion']['love'],
        disgust_score=analysis_result['emotion']['disgust'],
        relief_score=analysis_result['emotion']['relief'],
        gratitude_score=analysis_result['emotion']['gratitude'],
        confusion_score=analysis_result['emotion']['confusion']
    ))
    db.commit()
    
    return analysis_result