"""
Predictions API routes
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import date
from database import get_db_manager
from analytics import TrafficPredictor

router = APIRouter()

def get_predictor():
    return TrafficPredictor(get_db_manager())


@router.get("/traffic")
async def get_traffic_predictions(
    date_param: Optional[str] = Query(None, alias="date"),
    days_ahead: int = Query(1, ge=1, le=7)
):
    """Get traffic predictions"""
    try:
        predictor = get_predictor()
        db_manager = get_db_manager()
        target_date = date.fromisoformat(date_param) if date_param else date.today()
        
        # Get predictions from database
        predictions = db_manager.get_predictions_for_date(target_date)
        
        # If no predictions exist, generate new ones
        if not predictions:
            new_predictions = predictor.predict_with_prophet(days_ahead)
            predictor.save_predictions_to_db(new_predictions)
            predictions = db_manager.get_predictions_for_date(target_date)
        
        return {
            "success": True,
            "date": target_date.isoformat(),
            "data": predictions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/peak-hours")
async def get_peak_hour_predictions(date_param: Optional[str] = Query(None, alias="date")):
    """Get predicted peak hours"""
    try:
        target_date = date.fromisoformat(date_param) if date_param else date.today()
        peak_predictions = get_predictor().get_peak_predictions(target_date)
        
        return {
            "success": True,
            "date": target_date.isoformat(),
            "data": peak_predictions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate")
async def generate_predictions(days_ahead: int = Query(1, ge=1, le=7)):
    """Generate new predictions"""
    try:
        predictor = get_predictor()
        predictions = predictor.predict_with_prophet(days_ahead)
        predictor.save_predictions_to_db(predictions)
        
        return {
            "success": True,
            "message": f"Generated {len(predictions)} predictions",
            "data": predictions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
