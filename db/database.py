from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# from ..config import get_database_url
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_database_url

# Create declarative base instance
Base = declarative_base()

# Create SQLAlchemy engine with the connection string from config
engine = create_engine(
    get_database_url(),
    echo=False,  # Set to True to see SQL queries in logs
    pool_pre_ping=True,  # Detect disconnections
    pool_recycle=3600,  # Recycle connections after an hour
)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """
    Dependency for getting a database session.
    
    Usage:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            # Use the db session here
            pass
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    # Import models to ensure they are registered with Base before creating tables
    from .models import Role, User, RecommendationTypeModel, Recommendation, Journal, WeeklyReport
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)


def create_initial_data(db: Session):
    """
    Seed the database with initial data.
    This function should be called after init_db() and only if the database is empty.
    """
    from .models import Role, RecommendationTypeModel
    from .db_enum import UserRole, RecommendationType
    import logging
    
    # Create user roles if they don't exist
    for role in UserRole:
        existing_role = db.query(Role).filter(Role.role_type == role).first()
        if not existing_role:
            db.add(Role(role_type=role))
            logging.info(f"Created role: {role.value}")
    
    # Create recommendation types if they don't exist
    for recco_type in RecommendationType:
        existing_type = db.query(RecommendationTypeModel).filter(
            RecommendationTypeModel.recommendation_type == recco_type
        ).first()
        if not existing_type:
            db.add(RecommendationTypeModel(recommendation_type=recco_type))
            logging.info(f"Created recommendation type: {recco_type.value}")
    
    db.commit()
