from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, Dict, Any, List

class VisitorData(BaseModel):
    """Visitor data from entrance camera"""
    visitor_count: int = Field(..., ge=0)
    timestamp: datetime = Field(default_factory=datetime.now)
    date_val: date = Field(default_factory=date.today)
    hour: int = Field(..., ge=0, le=23)

class SectionAnalytics(BaseModel):
    """Section-wise analytics data"""
    section_name: str
    visitor_count: int = Field(..., ge=0)
    male_count: int = Field(default=0, ge=0)
    female_count: int = Field(default=0, ge=0)
    heatmap_data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    date_val: date = Field(default_factory=date.today)
    hour: int = Field(..., ge=0, le=23)

class CashierAnalytics(BaseModel):
    """Cashier performance analytics"""
    queue_length: int = Field(..., ge=0)
    estimated_wait_time: Optional[float] = Field(default=0.0, ge=0)
    is_busy: bool = False
    estimated_transactions: int = Field(default=0, ge=0)
    timestamp: datetime = Field(default_factory=datetime.now)
    date_val: date = Field(default_factory=date.today)
    hour: int = Field(..., ge=0, le=23)

class TrafficPrediction(BaseModel):
    """Traffic prediction data"""
    prediction_date: date
    prediction_hour: int = Field(..., ge=0, le=23)
    predicted_visitors: int = Field(..., ge=0)
    confidence_level: Optional[float] = Field(default=0.0, ge=0, le=1)
    model_used: str = "prophet"

class Recommendation(BaseModel):
    """AI-generated recommendation"""
    recommendation_type: str
    title: str
    description: str
    priority: str = Field(default="medium")
    timestamp: datetime = Field(default_factory=datetime.now)
    is_active: bool = True

class ChatbotQuery(BaseModel):
    """Chatbot query from user"""
    query: str
    language: str = "en"  # en or ar

class ChatbotResponse(BaseModel):
    """Chatbot response"""
    response: str
    recommendations: Optional[List[str]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class AnalyticsSummary(BaseModel):
    """Summary analytics response"""
    total_visitors: int
    current_queue_length: int
    peak_hour: int
    busiest_section: str
    conversion_rate: float
    timestamp: datetime = Field(default_factory=datetime.now)

class HeatmapData(BaseModel):
    """Heatmap data structure"""
    zones: Dict[str, int]  # zone_name: density
    timestamp: datetime = Field(default_factory=datetime.now)
