"""
Traffic prediction using time-series forecasting
"""
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrafficPredictor:
    """Predicts future traffic using time-series models"""
    
    def __init__(self, db_manager):
        """
        Initialize traffic predictor
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        logger.info("Traffic predictor initialized")
    
    def prepare_historical_data(self, days_back: int = 30) -> pd.DataFrame:
        """
        Prepare historical data for training
        
        Args:
            days_back: Number of days of historical data to use
        
        Returns:
            DataFrame with historical visitor data
        """
        try:
            data_points = []
            
            for i in range(days_back):
                target_date = date.today() - timedelta(days=i)
                visitors_data = self.db_manager.get_visitors_by_date(target_date)
                
                for record in visitors_data:
                    data_points.append({
                        'ds': datetime.combine(record['date'], datetime.min.time()) + timedelta(hours=record['hour']),
                        'y': record['visitor_count']
                    })
            
            if not data_points:
                logger.warning("No historical data available for prediction")
                return pd.DataFrame(columns=['ds', 'y'])
            
            df = pd.DataFrame(data_points)
            df = df.sort_values('ds')
            
            return df
        
        except Exception as e:
            logger.error(f"Error preparing historical data: {e}")
            return pd.DataFrame(columns=['ds', 'y'])
    
    def predict_with_prophet(self, days_ahead: int = 1) -> List[Dict]:
        """
        Predict traffic using Facebook Prophet
        
        Args:
            days_ahead: Number of days to predict ahead
        
        Returns:
            List of predictions
        """
        try:
            from prophet import Prophet
            
            # Prepare data
            df = self.prepare_historical_data()
            
            if df.empty:
                logger.warning("No data available for Prophet prediction")
                return self._generate_dummy_predictions(days_ahead)
            
            # Train model
            model = Prophet(
                daily_seasonality=True,
                weekly_seasonality=True,
                yearly_seasonality=False
            )
            model.fit(df)
            
            # Make predictions
            future = model.make_future_dataframe(periods=days_ahead * 24, freq='H')
            forecast = model.predict(future)
            
            # Extract predictions for future dates
            predictions = []
            start_date = datetime.now()
            
            for i in range(days_ahead * 24):
                pred_datetime = start_date + timedelta(hours=i)
                pred_row = forecast[forecast['ds'] >= pred_datetime].iloc[0]
                
                predictions.append({
                    'prediction_date': pred_datetime.date(),
                    'prediction_hour': pred_datetime.hour,
                    'predicted_visitors': max(0, int(pred_row['yhat'])),
                    'confidence_level': 0.85,
                    'model_used': 'prophet'
                })
            
            return predictions
        
        except ImportError:
            logger.warning("Prophet not available, using exponential smoothing")
            return self.predict_with_exponential_smoothing(days_ahead)
        except Exception as e:
            logger.error(f"Error in Prophet prediction: {e}")
            return self._generate_dummy_predictions(days_ahead)
    
    def predict_with_exponential_smoothing(self, days_ahead: int = 1) -> List[Dict]:
        """
        Predict traffic using exponential smoothing
        
        Args:
            days_ahead: Number of days to predict ahead
        
        Returns:
            List of predictions
        """
        try:
            df = self.prepare_historical_data()
            
            if df.empty:
                return self._generate_dummy_predictions(days_ahead)
            
            # Simple exponential smoothing
            alpha = 0.3
            predictions = []
            
            # Get last week's pattern
            last_week_avg = df.groupby(df['ds'].dt.hour)['y'].mean().to_dict()
            
            for i in range(days_ahead * 24):
                pred_datetime = datetime.now() + timedelta(hours=i)
                hour = pred_datetime.hour
                
                # Use last week's average for this hour
                base_prediction = last_week_avg.get(hour, 10)
                
                predictions.append({
                    'prediction_date': pred_datetime.date(),
                    'prediction_hour': hour,
                    'predicted_visitors': max(0, int(base_prediction)),
                    'confidence_level': 0.70,
                    'model_used': 'exponential_smoothing'
                })
            
            return predictions
        
        except Exception as e:
            logger.error(f"Error in exponential smoothing: {e}")
            return self._generate_dummy_predictions(days_ahead)
    
    def _generate_dummy_predictions(self, days_ahead: int = 1) -> List[Dict]:
        """
        Generate dummy predictions when no historical data is available
        
        Args:
            days_ahead: Number of days to predict
        
        Returns:
            List of dummy predictions
        """
        predictions = []
        
        # Typical retail traffic pattern
        hourly_pattern = {
            0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0,
            6: 2, 7: 5, 8: 8, 9: 12, 10: 15, 11: 18,
            12: 20, 13: 22, 14: 20, 15: 18, 16: 20,
            17: 25, 18: 28, 19: 22, 20: 15, 21: 10,
            22: 5, 23: 2
        }
        
        for i in range(days_ahead * 24):
            pred_datetime = datetime.now() + timedelta(hours=i)
            hour = pred_datetime.hour
            
            predictions.append({
                'prediction_date': pred_datetime.date(),
                'prediction_hour': hour,
                'predicted_visitors': hourly_pattern.get(hour, 10),
                'confidence_level': 0.60,
                'model_used': 'pattern_based'
            })
        
        return predictions
    
    def save_predictions_to_db(self, predictions: List[Dict]):
        """
        Save predictions to database
        
        Args:
            predictions: List of prediction dictionaries
        """
        try:
            for pred in predictions:
                self.db_manager.insert_prediction(
                    prediction_date=pred['prediction_date'],
                    prediction_hour=pred['prediction_hour'],
                    predicted_visitors=pred['predicted_visitors'],
                    confidence_level=pred['confidence_level'],
                    model_used=pred['model_used']
                )
            
            logger.info(f"Saved {len(predictions)} predictions to database")
        
        except Exception as e:
            logger.error(f"Error saving predictions: {e}")
    
    def get_peak_predictions(self, target_date: date = None) -> List[Dict]:
        """
        Get predicted peak hours for a date
        
        Args:
            target_date: Date to get predictions for
        
        Returns:
            List of peak hour predictions
        """
        if target_date is None:
            target_date = date.today()
        
        try:
            predictions = self.db_manager.get_predictions_for_date(target_date)
            
            # Sort by predicted visitors
            sorted_predictions = sorted(
                predictions,
                key=lambda x: x['predicted_visitors'],
                reverse=True
            )
            
            return sorted_predictions[:5]  # Top 5 peak hours
        
        except Exception as e:
            logger.error(f"Error getting peak predictions: {e}")
            return []
