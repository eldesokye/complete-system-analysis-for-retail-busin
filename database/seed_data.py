
import sys
import os
import random
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import Json
import logging

# Add parent directory to path
sys.path.append(os.getcwd())

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SECTIONS = ["Men's Clothing", "Women's Clothing", "Electronics", "Home & Garden", "Sports"]
OBJECTS = ["cell phone", "handbag", "backpack", "suitcase", "tie"]

def seed_database():
    """Seed database with demo data for the last 7 days"""
    conn = None
    try:
        logger.info("Connecting to database for seeding...")
        conn = psycopg2.connect(dsn=settings.database_url)
        cursor = conn.cursor()
        
        # Check if we already have data to avoid duplication/bloat
        cursor.execute("SELECT count(*) FROM visitors")
        count = cursor.fetchone()[0]
        if count > 100:
            logger.info(f"Database already has {count} records. Skipping seed.")
            return

        logger.info("Generating demo data...")
        
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        
        total_visitors_inserted = 0
        
        # Iterate through days
        current_date = start_date
        while current_date <= end_date:
            logger.info(f"Generating data for {current_date}")
            
            # Simulate store hours (9 AM to 9 PM)
            for hour in range(9, 21):
                # 1. Visitors (Entrance)
                # More visitors on weekends (5=Sat, 6=Sun) and evening hours
                is_weekend = current_date.weekday() >= 5
                base_visitors = random.randint(20, 50) if is_weekend else random.randint(10, 30)
                if 17 <= hour <= 19: # Peak hours
                    base_visitors = int(base_visitors * 1.5)
                
                cursor.execute(
                    "INSERT INTO visitors (visitor_count, timestamp, date, hour) VALUES (%s, %s, %s, %s)",
                    (base_visitors, datetime.combine(current_date, datetime.min.time().replace(hour=hour)), current_date, hour)
                )
                total_visitors_inserted += 1
                
                # 2. Section Analytics
                for section in SECTIONS:
                    # Random distribution of visitors to sections
                    section_visitors = int(base_visitors * random.uniform(0.1, 0.4))
                    male_count = int(section_visitors * random.uniform(0.4, 0.6))
                    female_count = section_visitors - male_count
                    
                    # Random objects
                    obj_counts = {obj: random.randint(0, 5) for obj in random.sample(OBJECTS, 2)}
                    
                    # Dummy heatmap data (just a placeholder structure)
                    heatmap = {"points": []}
                    
                    cursor.execute(
                        """
                        INSERT INTO section_analytics 
                        (section_name, visitor_count, male_count, female_count, object_counts, heatmap_data, timestamp, date, hour)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (section, section_visitors, male_count, female_count, Json(obj_counts), Json(heatmap), 
                         datetime.combine(current_date, datetime.min.time().replace(hour=hour)), current_date, hour)
                    )
                
                # 3. Cashier Analytics
                queue_length = random.randint(0, 8)
                wait_time = queue_length * random.uniform(1.5, 3.0) # ~2 mins per person
                transactions = int(base_visitors * random.uniform(0.3, 0.7)) # Conversion rate
                
                cursor.execute(
                    """
                    INSERT INTO cashier_analytics 
                    (queue_length, estimated_wait_time, is_busy, estimated_transactions, timestamp, date, hour)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (queue_length, wait_time, queue_length > 4, transactions, 
                     datetime.combine(current_date, datetime.min.time().replace(hour=hour)), current_date, hour)
                )

                # 4. Predictions (Future) - only for "today" to simulate readiness
                if current_date == end_date:
                    predicted = int(base_visitors * random.uniform(0.8, 1.2))
                    cursor.execute(
                        """
                        INSERT INTO traffic_predictions 
                        (prediction_date, prediction_hour, predicted_visitors, confidence_level, model_used)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (prediction_date, prediction_hour) DO NOTHING
                        """,
                        (current_date + timedelta(days=1), hour, predicted, 0.85, "prophet_v1")
                    )

            current_date += timedelta(days=1)

        conn.commit()
        logger.info(f"Seeding complete! Inserted ~{total_visitors_inserted} hourly records.")
        
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    seed_database()
