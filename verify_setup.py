
import sys
import os
import psycopg2
import logging

# Add parent directory to path
sys.path.append(os.getcwd())

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify():
    try:
        logger.info(f"Connecting to {settings.database_url.split('@')[1] if '@' in settings.database_url else 'DB'}...")
        conn = psycopg2.connect(dsn=settings.database_url)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = [row[0] for row in cursor.fetchall()]
        logger.info(f"Tables found: {tables}")
        
        required_tables = ['visitors', 'section_analytics', 'cashier_analytics', 'traffic_predictions', 'recommendations']
        missing = [t for t in required_tables if t not in tables]
        
        if missing:
            logger.error(f"Missing tables: {missing}")
        else:
            logger.info("All required tables present.")
            
        # Check views
        cursor.execute("SELECT table_name FROM information_schema.views WHERE table_schema = 'public'")
        views = [row[0] for row in cursor.fetchall()]
        logger.info(f"Views found: {views}")

        # Check data
        cursor.execute("SELECT count(*) FROM visitors")
        count = cursor.fetchone()[0]
        logger.info(f"Visitor records: {count}")
        
        if count > 0:
            logger.info("Database seeding successful!")
        else:
            logger.warning("Visitors table is empty.")
            
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        return False

if __name__ == "__main__":
    verify()
