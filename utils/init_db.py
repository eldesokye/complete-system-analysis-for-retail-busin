"""
Database initialization script
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database():
    """Initialize database schema"""
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            database=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            port=settings.DB_PORT
        )
        
        logger.info("Connected to PostgreSQL database")
        
        # Read schema file
        with open('database/schema.sql', 'r') as f:
            schema_sql = f.read()
        
        # Execute schema
        cursor = conn.cursor()
        cursor.execute(schema_sql)
        conn.commit()
        cursor.close()
        
        logger.info("Database schema initialized successfully")
        
        conn.close()
        
        return True
    
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False


if __name__ == "__main__":
    success = init_database()
    if success:
        print("✓ Database initialized successfully!")
        print("\nNext steps:")
        print("1. Run 'python utils/demo_data.py' to generate demo data")
        print("2. Run 'python main.py' to start the system")
    else:
        print("✗ Database initialization failed. Please check your PostgreSQL connection.")
