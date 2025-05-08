from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import date, timedelta, datetime
from fastapi.responses import JSONResponse
import json

from db.database import get_db
from db.models import User, WeeklyReport
from .utils import (
    get_user_journals_for_week, 
    format_journal_data_for_weekly_analysis,
    generate_weekly_analysis,
    generate_visualizations,
)
from utils.security import get_current_user

# Create router with prefix and tags defined here
router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


@router.get("/weekly-analysis", status_code=status.HTTP_200_OK) # Removed {user_id} from path
async def get_weekly_analysis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Add dependency
):
    """
    Generate a weekly analysis report based on the authenticated user's journal entries from the past 7 days
    """
    user_id = current_user.id # Use the authenticated user's ID
    
    # Get journal entries for the past 7 days
    journals = get_user_journals_for_week(db, user_id)
    
    if not journals:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No journal entries found for the past week"
        )
    
    # Format journal data for the weekly analysis
    formatted_data = format_journal_data_for_weekly_analysis(journals)
    
    # Generate weekly analysis
    analysis = generate_weekly_analysis(formatted_data)
    
    return analysis


@router.get("/weekly-visualizations", status_code=status.HTTP_200_OK) # Removed {user_id} from path
async def get_weekly_visualizations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) 
):
    """
    Generate visualizations for the authenticated user's journal entries from the past 7 days
    """
    user_id = current_user.id # Use the authenticated user's ID

    # Get journal entries for the past 7 days
    journals = get_user_journals_for_week(db, user_id)
    
    if not journals:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No journal entries found for the past week"
        )
    
    # Format journal data for the weekly analysis
    formatted_data = format_journal_data_for_weekly_analysis(journals)
    
    # Calculate cumulative scores for visualization
    raw_data = {
        "dates": [],
        "emotions": {
            "happiness": [], "sadness": [], "fear": [], "anger": [], 
            "surprise": [], "joy": [], "love": [], "disgust": [], 
            "relief": [], "gratitude": [], "confusion": []
        },
        "sentiments": {"positive": [], "negative": [], "neutral": []}
    }
    
    for entry in formatted_data:
        # Extract date (just the date part)
        date_str = entry["journal_timing"].split()[0]
        raw_data["dates"].append(date_str)
        
        # Extract emotion scores
        for emotion in raw_data["emotions"].keys():
            raw_data["emotions"][emotion].append(entry["emotion"][emotion])
        
        # Extract sentiment scores
        for sentiment in raw_data["sentiments"].keys():
            raw_data["sentiments"][sentiment].append(entry["sentiment"][sentiment])
    
    # Generate visualizations
    visualizations = generate_visualizations(raw_data)
    
    return JSONResponse(content=visualizations)


@router.get("/combined-weekly-report", status_code=status.HTTP_200_OK) # Keep status_code for successful GET
async def get_combined_weekly_report(
    # user_id: int,
    db: Session = Depends(get_db)
    # current_user: User = Depends(get_current_user)
):
    """
    Generate a combined weekly report with analysis and visualizations for the authenticated user
    and save it to the database.
    """
    # user_id = current_user.id
    user_id = 1
    # Get journal entries for the past 7 days
    journals = get_user_journals_for_week(db, user_id)
    
    if not journals:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No journal entries found for the past week to generate a report."
        )
    
    formatted_data = format_journal_data_for_weekly_analysis(journals)
    analysis = generate_weekly_analysis(formatted_data)
    
    if "raw_data" not in analysis:
        # Handle case where analysis might have failed or not produced raw_data
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate raw data for visualizations from analysis."
        )
    
    visualizations = generate_visualizations(analysis["raw_data"])
    
    # Prepare data for saving to WeeklyReport table
    today = datetime.utcnow().date()
    seven_days_ago = today - timedelta(days=6) # from_date should be start of the 7-day period

    # Create and save the weekly report
    new_weekly_report = WeeklyReport(
        user_id=user_id,
        from_date=seven_days_ago,
        to_date=today,
        report_response=json.dumps(analysis), # Save the full analysis object as JSON string
        visualizations=json.dumps(visualizations), # Save visualizations as JSON string
        created_at=datetime.utcnow()
    )
    
    db.add(new_weekly_report)
    db.commit()
    # db.refresh(new_weekly_report) # Optional, if you need the ID immediately

    # Prepare the response (as it was before)
    # Remove raw_data from the analysis part of the response to keep it clean
    if "raw_data" in analysis:
        del analysis["raw_data"]
    
    response_payload = {
        "analysis": analysis,
        "visualizations": visualizations
    }
    
    return JSONResponse(content=response_payload)