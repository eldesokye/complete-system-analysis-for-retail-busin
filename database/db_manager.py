from __future__ import annotations
"""
Database connection manager and CRUD operations
"""
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from psycopg2.pool import SimpleConnectionPool
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import logging
# Deferred import of settings to prevent circularity
def get_settings():
    from config import settings
    return settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Global instance (initially None, use get_db_manager)
db_manager = None


class DatabaseManager:
    """Manages PostgreSQL database connections and operations"""
    
    def __init__(self):
        """Initialize connection pool"""
        print(f"DEBUG: Initializing DatabaseManager, self id: {id(self)}")
        self.pool = None
        self.settings = get_settings()
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Create connection pool"""
        try:
            settings = get_settings()
            self.pool = SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=settings.DB_HOST,
                database=settings.DB_NAME,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                port=settings.DB_PORT
            )
            logger.info("Database connection pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create connection pool: {e}")
            raise
    
    def get_connection(self):
        """Get a connection from the pool"""
        return self.pool.getconn()
    
    def return_connection(self, conn):
        """Return connection to the pool"""
        self.pool.putconn(conn)
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = True) -> Optional[List[Dict]]:
        """Execute a query and return results"""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                if fetch:
                    result = cursor.fetchall()
                    return [dict(row) for row in result]
                conn.commit()
                return None
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Query execution failed: {e}")
            raise
        finally:
            if conn:
                self.return_connection(conn)
    
    # ==================== Visitor Operations ====================
    
    def insert_visitor_data(self, visitor_count: int, timestamp: datetime, date_val: date, hour: int):
        """Insert visitor data"""
        query = """
            INSERT INTO visitors (visitor_count, timestamp, date, hour)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """
        result = self.execute_query(query, (visitor_count, timestamp, date_val, hour), fetch=True)
        return result[0]['id'] if result else None
    
    def get_visitors_by_date(self, date_val: date) -> List[Dict]:
        """Get all visitor data for a specific date"""
        query = "SELECT * FROM visitors WHERE date = %s ORDER BY hour"
        return self.execute_query(query, (date_val,))
    
    def get_total_visitors_today(self) -> int:
        """Get total visitors for today"""
        query = "SELECT COALESCE(SUM(visitor_count), 0) as total FROM visitors WHERE date = CURRENT_DATE"
        result = self.execute_query(query)
        return result[0]['total'] if result else 0
    
    # ==================== Section Analytics Operations ====================
    
    def insert_section_analytics(self, section_name: str, visitor_count: int, male_count: int,
                                 female_count: int, heatmap_data: Dict, timestamp: datetime,
                                 date_val: date, hour: int):
        """Insert section analytics data"""
        query = """
            INSERT INTO section_analytics 
            (section_name, visitor_count, male_count, female_count, heatmap_data, timestamp, date, hour)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        result = self.execute_query(
            query,
            (section_name, visitor_count, male_count, female_count, Json(heatmap_data), timestamp, date_val, hour),
            fetch=True
        )
        return result[0]['id'] if result else None
    
    def get_section_analytics_by_date(self, date_val: date) -> List[Dict]:
        """Get section analytics for a specific date"""
        query = "SELECT * FROM section_analytics WHERE date = %s ORDER BY section_name, hour"
        return self.execute_query(query, (date_val,))
    
    def get_section_performance(self) -> List[Dict]:
        """Get section performance summary"""
        query = "SELECT * FROM section_performance WHERE date = CURRENT_DATE"
        return self.execute_query(query)
    
    # ==================== Cashier Analytics Operations ====================
    
    def insert_cashier_analytics(self, queue_length: int, estimated_wait_time: float,
                                is_busy: bool, estimated_transactions: int,
                                timestamp: datetime, date_val: date, hour: int):
        """Insert cashier analytics data"""
        query = """
            INSERT INTO cashier_analytics 
            (queue_length, estimated_wait_time, is_busy, estimated_transactions, timestamp, date, hour)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        result = self.execute_query(
            query,
            (queue_length, estimated_wait_time, is_busy, estimated_transactions, timestamp, date_val, hour),
            fetch=True
        )
        return result[0]['id'] if result else None
    
    def get_current_cashier_status(self) -> Dict:
        """Get current cashier status"""
        query = """
            SELECT * FROM cashier_analytics 
            ORDER BY timestamp DESC 
            LIMIT 1
        """
        result = self.execute_query(query)
        return result[0] if result else {}
    
    def get_cashier_analytics_by_date(self, date_val: date) -> List[Dict]:
        """Get cashier analytics for a specific date"""
        query = "SELECT * FROM cashier_analytics WHERE date = %s ORDER BY hour"
        return self.execute_query(query, (date_val,))
    
    # ==================== Prediction Operations ====================
    
    def insert_prediction(self, prediction_date: date, prediction_hour: int,
                         predicted_visitors: int, confidence_level: float, model_used: str):
        """Insert traffic prediction"""
        query = """
            INSERT INTO traffic_predictions 
            (prediction_date, prediction_hour, predicted_visitors, confidence_level, model_used)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (prediction_date, prediction_hour) 
            DO UPDATE SET 
                predicted_visitors = EXCLUDED.predicted_visitors,
                confidence_level = EXCLUDED.confidence_level,
                model_used = EXCLUDED.model_used,
                created_at = CURRENT_TIMESTAMP
            RETURNING id
        """
        result = self.execute_query(
            query,
            (prediction_date, prediction_hour, predicted_visitors, confidence_level, model_used),
            fetch=True
        )
        return result[0]['id'] if result else None
    
    def get_predictions_for_date(self, prediction_date: date) -> List[Dict]:
        """Get predictions for a specific date"""
        query = """
            SELECT * FROM traffic_predictions 
            WHERE prediction_date = %s 
            ORDER BY prediction_hour
        """
        return self.execute_query(query, (prediction_date,))
    
    # ==================== Recommendation Operations ====================
    
    def insert_recommendation(self, recommendation_type: str, title: str,
                            description: str, priority: str = "medium"):
        """Insert AI recommendation"""
        query = """
            INSERT INTO recommendations 
            (recommendation_type, title, description, priority)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """
        result = self.execute_query(query, (recommendation_type, title, description, priority), fetch=True)
        return result[0]['id'] if result else None
    
    def get_active_recommendations(self) -> List[Dict]:
        """Get all active recommendations"""
        query = """
            SELECT * FROM recommendations 
            WHERE is_active = TRUE 
            ORDER BY timestamp DESC
        """
        return self.execute_query(query)
    
    def deactivate_recommendation(self, recommendation_id: int):
        """Deactivate a recommendation"""
        query = "UPDATE recommendations SET is_active = FALSE WHERE id = %s"
        self.execute_query(query, (recommendation_id,), fetch=False)
    
    # ==================== Analytics & Summary Operations ====================
    
    def get_daily_summary(self, date_val: date = None) -> Dict:
        """Get daily summary"""
        if date_val is None:
            date_val = date.today()
        
        query = "SELECT * FROM daily_summary WHERE date = %s"
        result = self.execute_query(query, (date_val,))
        return result[0] if result else {}
    
    def get_peak_hours(self, date_val: date = None) -> List[Dict]:
        """Get peak hours for a date"""
        if date_val is None:
            date_val = date.today()
        
        query = """
            SELECT hour, SUM(visitor_count) as total_visitors
            FROM visitors
            WHERE date = %s
            GROUP BY hour
            ORDER BY total_visitors DESC
            LIMIT 5
        """
        return self.execute_query(query, (date_val,))
    
    def get_conversion_rate(self, date_val: date = None) -> float:
        """Calculate conversion rate (transactions / visitors)"""
        if date_val is None:
            date_val = date.today()
        
        query = """
            SELECT 
                COALESCE(SUM(v.visitor_count), 0) as total_visitors,
                COALESCE(SUM(c.estimated_transactions), 0) as total_transactions
            FROM visitors v
            LEFT JOIN cashier_analytics c ON v.date = c.date AND v.hour = c.hour
            WHERE v.date = %s
        """
        result = self.execute_query(query, (date_val,))
        if result and result[0]['total_visitors'] > 0:
            return result[0]['total_transactions'] / result[0]['total_visitors']
        return 0.0
    
    def close(self):
        """Close all connections in the pool"""
        if self.pool:
            self.pool.closeall()
            logger.info("Database connection pool closed")


# Helper to get database manager instance
_db_manager = None

def get_db_manager():
    """Get or create a global DatabaseManager instance"""
    global _db_manager
    print(f"DEBUG: get_db_manager called, current _db_manager: {_db_manager}")
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
