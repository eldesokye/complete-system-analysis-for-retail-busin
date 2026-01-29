from __future__ import annotations
"""
Chatbot API routes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import get_db_manager
from analytics import AnalyticsAggregator, TrafficPredictor
from chatbot import ChatbotService

router = APIRouter()

def get_chatbot_service():
    db_manager = get_db_manager()
    aggregator = AnalyticsAggregator(db_manager)
    predictor = TrafficPredictor(db_manager)
    return ChatbotService(db_manager, aggregator, predictor)


class ChatQuery(BaseModel):
    """Chat query request model"""
    query: str
    language: str = "en"
    session_id: str = "default"


class ChatResponse(BaseModel):
    """Chat response model"""
    success: bool
    response: str
    recommendations: list
    context: dict


@router.post("/query", response_model=ChatResponse)
async def chat_query(request: ChatQuery):
    """Send a query to the chatbot"""
    try:
        result = get_chatbot_service().query(
            user_query=request.query,
            language=request.language,
            session_id=request.session_id
        )
        
        return ChatResponse(
            success=True,
            response=result['response'],
            recommendations=result['recommendations'],
            context=result['context']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_chatbot_summary(language: str = "en"):
    """Get automated summary from chatbot"""
    try:
        summary = get_chatbot_service().get_summary(language)
        
        return {
            "success": True,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations")
async def get_recommendations():
    """Get AI-generated recommendations"""
    try:
        recommendations = get_chatbot_service().generate_recommendations()
        
        return {
            "success": True,
            "data": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active-recommendations")
async def get_active_recommendations():
    """Get active recommendations from database"""
    try:
        recommendations = get_db_manager().get_active_recommendations()
        
        return {
            "success": True,
            "data": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/history/{session_id}")
async def clear_conversation_history(session_id: str):
    """Clear conversation history for a session"""
    try:
        get_chatbot_service().clear_history(session_id)
        
        return {
            "success": True,
            "message": f"Conversation history cleared for session: {session_id}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
