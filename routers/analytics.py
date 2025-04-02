from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import date, timedelta
from fastapi.responses import JSONResponse

from db.database import get_db
from .utils import (
    get_user_journals_for_week, 
    format_journal_data_for_weekly_analysis,
    generate_weekly_analysis,
    generate_visualizations,
    VISUALIZATION_DIR
)

# Create router with prefix and tags defined here
router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


@router.get("/weekly-analysis/{user_id}", status_code=status.HTTP_200_OK)
async def get_weekly_analysis(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate a weekly analysis report based on the user's journal entries from the past 7 days
    """
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


@router.get("/weekly-visualizations/{user_id}", status_code=status.HTTP_200_OK)
async def get_weekly_visualizations(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate visualizations for the user's journal entries from the past 7 days
    """
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


@router.get("/combined-weekly-report/{user_id}", status_code=status.HTTP_200_OK)
async def get_combined_weekly_report(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate a combined weekly report with analysis and visualizations
    """
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
    
    # Generate visualizations using the raw_data from the analysis
    visualizations = generate_visualizations(analysis["raw_data"])
    
    # Remove raw_data from the response to keep it clean
    del analysis["raw_data"]
    
    # Create response with analysis and visualizations
    response = {
        "analysis": analysis,
        "visualizations": visualizations
    }
    
    return JSONResponse(content=response)