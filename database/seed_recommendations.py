
import sys
import os
import psycopg2
import logging
from datetime import datetime

# Add parent directory to path
sys.path.append(os.getcwd())

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_recommendations():
    """Seed database with initial recommendations"""
    conn = None
    try:
        logger.info("Connecting to database...")
        conn = psycopg2.connect(dsn=settings.database_url)
        cursor = conn.cursor()
        
        # Check if active recommendations already exist
        cursor.execute("SELECT count(*) FROM recommendations WHERE is_active = TRUE")
        count = cursor.fetchone()[0]
        
        if count > 0:
            logger.info(f"Found {count} active recommendations. Skipping seed.")
            return

        logger.info("Seeding recommendations...")
        
        recommendations = [
            {
                'type': 'staffing',
                'title': 'High Weekend Traffic Expected',
                'description': 'Historical data indicates a 40% increase in visitors this Saturday. Schedule 2 extra staff members.',
                'priority': 'high'
            },
            {
                'type': 'layout',
                'title': 'Underperforming Section: Home & Garden',
                'description': 'Visitor dwell time in Home & Garden is 30% below average. Consider rearranging the display at the entrance.',
                'priority': 'medium'
            },
            {
                'type': 'inventory',
                'title': 'Low Stock Alert: Electronics',
                'description': 'High conversion rate in Electronics suggests potential stock shortages. Verify inventory levels.',
                'priority': 'medium'
            },
            {
                'type': 'promotion',
                'title': 'Cross-selling Opportunity',
                'description': 'High correlation between Sports and Men\'s Clothing. Consider a bundle promotion.',
                'priority': 'low'
            }
        ]
        
        timestamp = datetime.now()
        
        for rec in recommendations:
            cursor.execute(
                """
                INSERT INTO recommendations 
                (recommendation_type, title, description, priority, is_active, timestamp)
                VALUES (%s, %s, %s, %s, TRUE, %s)
                """,
                (rec['type'], rec['title'], rec['description'], rec['priority'], timestamp)
            )
            
        conn.commit()
        logger.info(f"Successfully inserted {len(recommendations)} recommendations.")
        
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    seed_recommendations()
