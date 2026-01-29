"""
Demo data generator for testing and development
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from datetime import datetime, date, timedelta
from database import get_db_manager
from analytics import TrafficPredictor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DemoDataGenerator:
    """Generates realistic demo data for the retail analytics system"""
    
    def __init__(self):
        """Initialize demo data generator"""
        self.sections = ["Men's Clothing", "Women's Clothing", "Accessories", "Shoes", "Kids Section"]
        self.db_manager = get_db_manager()
        logger.info("Demo data generator initialized")
    
    def generate_visitor_data(self, days_back: int = 7):
        """
        Generate visitor data for the past N days
        
        Args:
            days_back: Number of days to generate data for
        """
        logger.info(f"Generating visitor data for {days_back} days...")
        
        # Typical hourly patterns (0-23 hours)
        hourly_pattern = {
            0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0,
            6: 2, 7: 5, 8: 8, 9: 12, 10: 15, 11: 18,
            12: 20, 13: 22, 14: 20, 15: 18, 16: 20,
            17: 25, 18: 28, 19: 22, 20: 15, 21: 10,
            22: 5, 23: 2
        }
        
        for day_offset in range(days_back):
            target_date = date.today() - timedelta(days=day_offset)
            
            # Weekend multiplier
            is_weekend = target_date.weekday() >= 5
            multiplier = 1.5 if is_weekend else 1.0
            
            for hour in range(24):
                base_visitors = hourly_pattern.get(hour, 0)
                visitor_count = int(base_visitors * multiplier * random.uniform(0.8, 1.2))
                
                if visitor_count > 0:
                    timestamp = datetime.combine(target_date, datetime.min.time()) + timedelta(hours=hour)
                    
                    self.db_manager.insert_visitor_data(
                        visitor_count=visitor_count,
                        timestamp=timestamp,
                        date_val=target_date,
                        hour=hour
                    )
        
        logger.info(f"Generated visitor data for {days_back} days")
    
    def generate_section_data(self, days_back: int = 7):
        """
        Generate section analytics data
        
        Args:
            days_back: Number of days to generate data for
        """
        logger.info(f"Generating section data for {days_back} days...")
        
        for day_offset in range(days_back):
            target_date = date.today() - timedelta(days=day_offset)
            
            for hour in range(9, 22):  # Store hours: 9 AM to 10 PM
                for section in self.sections:
                    visitor_count = random.randint(5, 30)
                    male_count = random.randint(0, visitor_count)
                    female_count = visitor_count - male_count
                    
                    # Generate heatmap data
                    heatmap_data = {
                        f"zone_{i}_{j}": random.randint(0, 100)
                        for i in range(3)
                        for j in range(3)
                    }
                    
                    timestamp = datetime.combine(target_date, datetime.min.time()) + timedelta(hours=hour)
                    
                    self.db_manager.insert_section_analytics(
                        section_name=section,
                        visitor_count=visitor_count,
                        male_count=male_count,
                        female_count=female_count,
                        heatmap_data=heatmap_data,
                        timestamp=timestamp,
                        date_val=target_date,
                        hour=hour
                    )
        
        logger.info(f"Generated section data for {days_back} days")
    
    def generate_cashier_data(self, days_back: int = 7):
        """
        Generate cashier analytics data
        
        Args:
            days_back: Number of days to generate data for
        """
        logger.info(f"Generating cashier data for {days_back} days...")
        
        for day_offset in range(days_back):
            target_date = date.today() - timedelta(days=day_offset)
            
            for hour in range(9, 22):
                queue_length = random.randint(0, 10)
                estimated_wait_time = queue_length * 120.0  # 2 minutes per person
                is_busy = queue_length >= 3
                estimated_transactions = random.randint(5, 20)
                
                timestamp = datetime.combine(target_date, datetime.min.time()) + timedelta(hours=hour)
                
                self.db_manager.insert_cashier_analytics(
                    queue_length=queue_length,
                    estimated_wait_time=estimated_wait_time,
                    is_busy=is_busy,
                    estimated_transactions=estimated_transactions,
                    timestamp=timestamp,
                    date_val=target_date,
                    hour=hour
                )
        
        logger.info(f"Generated cashier data for {days_back} days")
    
    def generate_predictions(self, days_ahead: int = 3):
        """
        Generate traffic predictions
        
        Args:
            days_ahead: Number of days to predict ahead
        """
        logger.info(f"Generating predictions for {days_ahead} days...")
        
        predictor = TrafficPredictor(self.db_manager)
        predictions = predictor.predict_with_prophet(days_ahead)
        predictor.save_predictions_to_db(predictions)
        
        logger.info(f"Generated {len(predictions)} predictions")
    
    def generate_recommendations(self):
        """Generate sample recommendations"""
        logger.info("Generating sample recommendations...")
        
        recommendations = [
            {
                'type': 'staffing',
                'title': 'Peak Hour Staffing',
                'description': 'Consider adding 2 more staff members during peak hours (5 PM - 8 PM)',
                'priority': 'high'
            },
            {
                'type': 'layout',
                'title': 'Optimize Kids Section',
                'description': 'Kids Section shows low traffic. Consider relocating to a more visible area.',
                'priority': 'medium'
            },
            {
                'type': 'cashier',
                'title': 'Additional Cashier Lane',
                'description': 'Queue length frequently exceeds 5 people. Opening an additional lane recommended.',
                'priority': 'high'
            },
            {
                'type': 'marketing',
                'title': 'Morning Promotions',
                'description': 'Low traffic in morning hours (9 AM - 11 AM). Consider special promotions.',
                'priority': 'low'
            }
        ]
        
        for rec in recommendations:
            self.db_manager.insert_recommendation(
                recommendation_type=rec['type'],
                title=rec['title'],
                description=rec['description'],
                priority=rec['priority']
            )
        
        logger.info(f"Generated {len(recommendations)} recommendations")
    
    def generate_all(self, days_back: int = 7, days_ahead: int = 3):
        """
        Generate all demo data
        
        Args:
            days_back: Days of historical data
            days_ahead: Days of predictions
        """
        logger.info("Generating all demo data...")
        
        self.generate_visitor_data(days_back)
        self.generate_section_data(days_back)
        self.generate_cashier_data(days_back)
        self.generate_predictions(days_ahead)
        self.generate_recommendations()
        
        logger.info("All demo data generated successfully!")


if __name__ == "__main__":
    db_manager = get_db_manager()
    generator = DemoDataGenerator()
    generator.generate_all(days_back=7, days_ahead=3)
