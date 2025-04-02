from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class EmotionScores(BaseModel):
    happiness: int
    sadness: int
    fear: int
    anger: int
    surprise: int
    joy: int
    love: int
    disgust: int
    relief: int
    gratitude: int
    confusion: int


class SentimentScores(BaseModel):
    positive: int
    negative: int
    neutral: int


class JournalData(BaseModel):
    journal_content: str
    response: Optional[str] = None
    emotion: EmotionScores
    sentiment: SentimentScores
    journal_timing: str


class DominantDay(BaseModel):
    day: str
    emotions: List[str]


class WeeklyEmotionAnalysis(BaseModel):
    dominant_emotions: List[str]
    highest_positive_day: DominantDay
    highest_negative_day: DominantDay
    emotional_patterns: str
    trajectory: str


class WeeklySentimentAnalysis(BaseModel):
    overall_sentiment: str
    significant_shifts: List[str]
    influencing_factors: List[str]
    general_mood: str


class ProgressAssessment(BaseModel):
    growth_areas: List[str]
    challenges: List[str]
    consistent_patterns: List[str]
    improvement_suggestions: List[str]


class CumulativeScores(BaseModel):
    emotion: EmotionScores
    sentiment: SentimentScores


class WeeklyAnalysisResponse(BaseModel):
    weekly_emotion_analysis: WeeklyEmotionAnalysis
    weekly_sentiment_analysis: WeeklySentimentAnalysis
    progress_assessment: ProgressAssessment
    weekly_summary: str
    cumulative_scores: CumulativeScores


class Visualizations(BaseModel):
    emotion_line_plot: str
    sentiment_line_plot: str
    emotion_radar_chart: str


class CombinedWeeklyReport(BaseModel):
    analysis: WeeklyAnalysisResponse
    visualizations: Visualizations

