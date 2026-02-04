"""
Analytics aggregator and metrics calculation
"""
from typing import Dict, List
from datetime import date, datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalyticsAggregator:
    """Aggregates and calculates analytics metrics"""
    
    def __init__(self, db_manager):
        """
        Initialize analytics aggregator
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        logger.info("Analytics aggregator initialized")
    
    def get_live_summary(self) -> Dict:
        """Get real-time summary of current store status"""
        try:
            # Get current cashier status
            cashier_status = self.db_manager.get_current_cashier_status()
            
            # Get today's total visitors
            total_visitors = self.db_manager.get_total_visitors_today()
            
            # Get section performance
            section_performance = self.db_manager.get_section_performance()
            
            # Find busiest section
            busiest_section = "N/A"
            max_visitors = 0
            if section_performance:
                for section in section_performance:
                    if section.get('total_visitors', 0) > max_visitors:
                        max_visitors = section['total_visitors']
                        busiest_section = section['section_name']
            
            # Get peak hours
            peak_hours = self.db_manager.get_peak_hours()
            peak_hour = peak_hours[0]['hour'] if peak_hours else datetime.now().hour
            
            # Get conversion rate
            conversion_rate = self.db_manager.get_conversion_rate()

            # Get average dwell time
            avg_dwell = self.db_manager.get_average_dwell_time(date_val=date.today())
            
            return {
                'total_visitors': total_visitors,
                'current_queue_length': cashier_status.get('queue_length', 0),
                'is_cashier_busy': cashier_status.get('is_busy', False),
                'estimated_wait_time': cashier_status.get('estimated_wait_time', 0),
                'peak_hour': peak_hour,
                'busiest_section': busiest_section,
                'conversion_rate': round(conversion_rate * 100, 2),
                'avg_dwell_time_sec': round(avg_dwell, 1),
                'timestamp': datetime.now()
            }
        
        except Exception as e:
            logger.error(f"Error getting live summary: {e}")
            return {}
    
    def get_hourly_breakdown(self, target_date: date = None) -> List[Dict]:
        """Get hourly breakdown of visitors"""
        if target_date is None:
            target_date = date.today()
        
        try:
            visitors_data = self.db_manager.get_visitors_by_date(target_date)
            
            # Group by hour
            hourly_data = {}
            for record in visitors_data:
                hour = record['hour']
                if hour not in hourly_data:
                    hourly_data[hour] = {
                        'hour': hour,
                        'visitor_count': 0
                    }
                hourly_data[hour]['visitor_count'] += record['visitor_count']
            
            return sorted(hourly_data.values(), key=lambda x: x['hour'])
        
        except Exception as e:
            logger.error(f"Error getting hourly breakdown: {e}")
            return []
    
    def get_section_comparison(self, target_date: date = None) -> List[Dict]:
        """Compare performance across sections"""
        if target_date is None:
            target_date = date.today()
        
        try:
            section_data = self.db_manager.get_section_analytics_by_date(target_date)
            
            # Aggregate by section
            section_totals = {}
            for record in section_data:
                section_name = record['section_name']
                if section_name not in section_totals:
                    section_totals[section_name] = {
                        'section_name': section_name,
                        'total_visitors': 0,
                        'male_count': 0,
                        'female_count': 0
                    }
                
                section_totals[section_name]['total_visitors'] += record['visitor_count']
                section_totals[section_name]['male_count'] += record.get('male_count', 0)
                section_totals[section_name]['female_count'] += record.get('female_count', 0)
                
                # Aggregate object counts
                if record.get('object_counts'):
                    # Ensure it's a dict (psycopg2 might return string/dict depending on version/config)
                    # Helper assumes it's dict-like
                    objs = record['object_counts']
                    current_objs = section_totals[section_name].get('object_counts', {})
                    for obj_name, count in objs.items():
                        current_objs[obj_name] = current_objs.get(obj_name, 0) + count
                    section_totals[section_name]['object_counts'] = current_objs
            
            return sorted(
                section_totals.values(),
                key=lambda x: x['total_visitors'],
                reverse=True
            )
        
        except Exception as e:
            logger.error(f"Error getting section comparison: {e}")
            return []
    
    def get_cashier_performance(self, target_date: date = None) -> Dict:
        """Get cashier performance metrics"""
        if target_date is None:
            target_date = date.today()
        
        try:
            cashier_data = self.db_manager.get_cashier_analytics_by_date(target_date)
            
            if not cashier_data:
                return {}
            
            total_transactions = sum(record.get('estimated_transactions', 0) for record in cashier_data)
            avg_queue_length = sum(record['queue_length'] for record in cashier_data) / len(cashier_data)
            max_queue_length = max(record['queue_length'] for record in cashier_data)
            busy_periods = sum(1 for record in cashier_data if record.get('is_busy', False))
            
            return {
                'total_transactions': total_transactions,
                'average_queue_length': round(avg_queue_length, 2),
                'max_queue_length': max_queue_length,
                'busy_periods': busy_periods,
                'total_records': len(cashier_data)
            }
        
        except Exception as e:
            logger.error(f"Error getting cashier performance: {e}")
            return {}
    
    def identify_underperforming_sections(self, threshold_percentile: float = 0.3) -> List[str]:
        """Identify sections with low traffic"""
        try:
            section_comparison = self.get_section_comparison()
            
            if not section_comparison:
                return []
            
            # Calculate threshold
            visitor_counts = [s['total_visitors'] for s in section_comparison]
            avg_visitors = sum(visitor_counts) / len(visitor_counts)
            threshold = avg_visitors * threshold_percentile
            
            # Find underperforming sections
            underperforming = [
                s['section_name']
                for s in section_comparison
                if s['total_visitors'] < threshold
            ]
            
            return underperforming
        
        except Exception as e:
            logger.error(f"Error identifying underperforming sections: {e}")
            return []
    
    def get_traffic_timeline(self, days: int = 7) -> List[Dict]:
        """Get traffic timeline for the past N days"""
        try:
            timeline = []
            
            for i in range(days):
                target_date = date.today() - timedelta(days=i)
                daily_summary = self.db_manager.get_daily_summary(target_date)
                
                if daily_summary:
                    timeline.append({
                        'date': target_date.isoformat(),
                        'total_visitors': daily_summary.get('total_visitors', 0),
                        'avg_hourly_visitors': daily_summary.get('avg_hourly_visitors', 0),
                        'peak_visitors': daily_summary.get('peak_visitors', 0)
                    })
            
            return sorted(timeline, key=lambda x: x['date'])
        
        except Exception as e:
            logger.error(f"Error getting traffic timeline: {e}")
            return []
