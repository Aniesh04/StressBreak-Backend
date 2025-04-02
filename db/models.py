from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, Boolean, Date, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from .db_enum import RecommendationType, UserRole
from .abstract import BasicModel

class Role(BasicModel):
    """Role model representing user roles"""
    __tablename__ = "roles"
    
    role_type = Column(Enum(UserRole), nullable=False)
    
    # Relationships
    users = relationship("User", back_populates="role")
    
    def __repr__(self):
        return f"<Role(id={self.id}, role_type={self.role_type.value})>"


class User(BasicModel):
    """User model for application users"""
    __tablename__ = "users"
    
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    date_joined = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    role = relationship("Role", back_populates="users")
    journals = relationship("Journal", back_populates="user")
    weekly_reports = relationship("WeeklyReport", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, email={self.email})>"


class RecommendationTypeModel(BasicModel):
    """Recommendation type model"""
    __tablename__ = "recommendation_types"
    
    recommendation_type = Column(Enum(RecommendationType), nullable=False, unique=True)
    
    # Relationships
    recommendations = relationship("Recommendation", back_populates="recommendation_type")
    
    def __repr__(self):
        return f"<RecommendationTypeModel(id={self.id}, type={self.recommendation_type.value})>"


class Recommendation(BasicModel):
    """Recommendation model for music, food, exercises, movies"""
    __tablename__ = "recommendations"
    
    ref_url = Column(String(255), nullable=False)
    recco_category = Column(Integer, ForeignKey("recommendation_types.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    recommendation_type = relationship("RecommendationTypeModel", back_populates="recommendations")
    
    def __repr__(self):
        return f"<Recommendation(id={self.id}, title={self.title}, category_id={self.recco_category})>"


class Journal(BasicModel):
    """Journal model for user entries and sentiment analysis"""
    __tablename__ = "journals"
    
    journal_content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Sentiment scores
    positive_score = Column(Integer, default=0)
    negative_score = Column(Integer, default=0)
    neutral_score = Column(Integer, default=0)
    
    # Emotion scores
    happiness_score = Column(Integer, default=0)
    sadness_score = Column(Integer, default=0)
    fear_score = Column(Integer, default=0)
    anger_score = Column(Integer, default=0)
    surprise_score = Column(Integer, default=0)
    joy_score = Column(Integer, default=0)
    love_score = Column(Integer, default=0)
    disgust_score = Column(Integer, default=0)
    relief_score = Column(Integer, default=0)
    gratitude_score = Column(Integer, default=0)
    confusion_score = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="journals")
    
    def __repr__(self):
        return f"<Journal(id={self.id}, user_id={self.user_id}, created_at={self.created_at})>"


class WeeklyReport(BasicModel):
    """Weekly report model for user progress tracking"""
    __tablename__ = "weekly_reports"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)
    report_response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="weekly_reports")
    
    def __repr__(self):
        return f"<WeeklyReport(id={self.id}, user_id={self.user_id}, from={self.from_date}, to={self.to_date})>"
