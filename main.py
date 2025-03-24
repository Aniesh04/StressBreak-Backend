import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Import database components
from db.database import init_db, get_db, create_initial_data, SessionLocal
from include_routers import include_all_routers

# Create FastAPI application
app = FastAPI(
    title="StressBreak API",
    description="API for StressBreak application - supporting mental well-being through journaling and recommendations",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
include_all_routers(app)

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Welcome to StressBreak API!",
        "status": "healthy",
        "version": "0.1.0",
    }

# Startup event - runs when the application starts
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Initializing database on application startup...")
    
    # Create all tables based on models
    init_db()
    logger.info("Database tables created or verified.")
    
    # Seed initial data (safe to run multiple times)
    db = SessionLocal()
    try:
        create_initial_data(db)
        logger.info("Initial data seeded successfully.")
    except Exception as e:
        logger.error(f"Error seeding initial data: {str(e)}")
    finally:
        db.close()
    
    logger.info("Database initialization complete.")

# Run the application
# if __name__ == "__main__":
#     import uvicorn
    
#     uvicorn.run(
#         "main:app",
#         host="0.0.0.0", 
#         port=8000,
#         reload=True,
#     )
