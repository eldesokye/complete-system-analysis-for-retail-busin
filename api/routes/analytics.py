"""
Analytics API routes
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import date, datetime
from database import get_db_manager
from analytics import AnalyticsAggregator

router = APIRouter()

def get_aggregator():
    return AnalyticsAggregator(get_db_manager())


@router.get("/live")
async def get_live_analytics():
    """Get real-time analytics summary"""
    try:
        aggregator = get_aggregator()
        summary = aggregator.get_live_summary()
        return {
            "success": True,
            "data": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sections")
async def get_section_analytics(date_param: Optional[str] = Query(None, alias="date")):
    """Get section-wise analytics"""
    try:
        aggregator = get_aggregator()
        target_date = date.fromisoformat(date_param) if date_param else date.today()
        sections = aggregator.get_section_comparison(target_date)
        
        return {
            "success": True,
            "date": target_date.isoformat(),
            "data": sections
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cashier")
async def get_cashier_analytics(date_param: Optional[str] = Query(None, alias="date")):
    """Get cashier performance analytics"""
    try:
        aggregator = get_aggregator()
        target_date = date.fromisoformat(date_param) if date_param else date.today()
        cashier_perf = aggregator.get_cashier_performance(target_date)
        
        return {
            "success": True,
            "date": target_date.isoformat(),
            "data": cashier_perf
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hourly")
async def get_hourly_breakdown(date_param: Optional[str] = Query(None, alias="date")):
    """Get hourly visitor breakdown"""
    try:
        aggregator = get_aggregator()
        target_date = date.fromisoformat(date_param) if date_param else date.today()
        hourly_data = aggregator.get_hourly_breakdown(target_date)
        
        return {
            "success": True,
            "date": target_date.isoformat(),
            "data": hourly_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_daily_summary(date_param: Optional[str] = Query(None, alias="date")):
    """Get daily summary"""
    try:
        target_date = date.fromisoformat(date_param) if date_param else date.today()
        summary = get_db_manager().get_daily_summary(target_date)
        
        return {
            "success": True,
            "date": target_date.isoformat(),
            "data": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/timeline")
async def get_traffic_timeline(days: int = Query(7, ge=1, le=30)):
    """Get traffic timeline for the past N days"""
    try:
        aggregator = get_aggregator()
        timeline = aggregator.get_traffic_timeline(days)
        
        return {
            "success": True,
            "days": days,
            "data": timeline
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/underperforming")
async def get_underperforming_sections():
    """Get list of underperforming sections"""
    try:
        aggregator = get_aggregator()
        sections = aggregator.identify_underperforming_sections()
        
        return {
            "success": True,
            "data": sections
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversion-rate")
async def get_conversion_rate(date_param: Optional[str] = Query(None, alias="date")):
    """Get conversion rate"""
    try:
        aggregator = get_aggregator()
        target_date = date.fromisoformat(date_param) if date_param else date.today()
        rate = get_db_manager().get_conversion_rate(target_date)
        
        return {
            "success": True,
            "date": target_date.isoformat(),
            "conversion_rate": round(rate * 100, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
