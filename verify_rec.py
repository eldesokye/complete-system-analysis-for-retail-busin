
import sys
import os
import psycopg2
import logging

# Add parent directory to path
sys.path.append(os.getcwd())

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_rec():
    try:
        conn = psycopg2.connect(dsn=settings.database_url)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM recommendations WHERE is_active = TRUE")
        rows = cursor.fetchall()
        
        logger.info(f"Found {len(rows)} active recommendations.")
        for row in rows:
            logger.info(f"- {row[2]}: {row[3]}") # title, description (guessing indices)
            
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        return False

if __name__ == "__main__":
    verify_rec()
