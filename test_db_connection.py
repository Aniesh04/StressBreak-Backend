"""
Database connection test script.
Run this to verify that your database connection works correctly.

This script is not required for normal application operation but is a useful utility
for manual testing. It performs the following:

1. Connects to the PostgreSQL database using SQLAlchemy
2. Executes a simple query to verify connectivity
3. Creates all database tables defined in the models
4. Seeds the database with initial reference data

Usage:
    python test_db_connection.py

Note: The same functionality runs automatically when the FastAPI server starts,
so running this separately is only needed for troubleshooting connectivity issues.
"""
import sys
import logging
from sqlalchemy import text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Import database components
try:
    from db.database import engine, init_db, create_initial_data, SessionLocal
    from config import get_database_url
    
    logger.info(f"Database URL: {get_database_url()}")
    
    # Test raw connection
    logger.info("Testing database connection...")
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        logger.info(f"Connection successful! Result: {result.fetchone()}")
    
    # Initialize database (create tables)
    logger.info("Initializing database schema...")
    init_db()
    logger.info("Database schema initialization complete.")
    
    # Seed initial data
    logger.info("Seeding initial data...")
    with SessionLocal() as db:
        create_initial_data(db)
    logger.info("Initial data seeding complete.")
    
    logger.info("Database setup complete and working correctly!")
    
except Exception as e:
    logger.error(f"Error connecting to database: {str(e)}")
    raise 