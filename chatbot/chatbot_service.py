"""
Chatbot service that integrates analytics and AI
"""
from typing import Dict, List, Optional
from datetime import date
import logging

from .groq_client import GroqClient
from .prompts import (
    SYSTEM_PROMPT_EN,
    SYSTEM_PROMPT_AR,
    format_analytics_context,
    format_prediction_context
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatbotService:
    """Intelligent chatbot service for retail analytics"""
    
    def __init__(self, db_manager, analytics_aggregator, traffic_predictor):
        """
        Initialize chatbot service
        
        Args:
            db_manager: Database manager instance
            analytics_aggregator: Analytics aggregator instance
            traffic_predictor: Traffic predictor instance
        """
        self.db_manager = db_manager
        self.analytics_aggregator = analytics_aggregator
        self.traffic_predictor = traffic_predictor
        self.groq_client = GroqClient()
        
        # Conversation history (in-memory, can be moved to DB)
        self.conversation_history: Dict[str, List[Dict]] = {}
        
        logger.info("Chatbot service initialized")
    
    def get_current_context(self) -> Dict:
        """Get current analytics context for the chatbot"""
        try:
            # Get live summary
            live_summary = self.analytics_aggregator.get_live_summary()
            
            # Get section comparison
            sections = self.analytics_aggregator.get_section_comparison()
            
            # Get predictions for today
            predictions = self.db_manager.get_predictions_for_date(date.today())
            
            # Get active recommendations
            recommendations = self.db_manager.get_active_recommendations()
            
            # Get cashier performance
            cashier_perf = self.analytics_aggregator.get_cashier_performance()
            
            return {
                **live_summary,
                'sections': sections,
                'predictions': predictions,
                'recommendations': recommendations,
                'cashier_performance': cashier_perf
            }
        
        except Exception as e:
            logger.error(f"Error getting current context: {e}")
            return {}
    
    def generate_recommendations(self) -> List[Dict]:
        """Generate AI-powered recommendations based on current data"""
        try:
            context = self.get_current_context()
            
            recommendations = []
            
            # Check for high queue
            if context.get('current_queue_length', 0) >= 5:
                recommendations.append({
                    'type': 'staffing',
                    'title': 'High Queue Detected',
                    'description': f"Queue length is {context['current_queue_length']}. Consider opening additional cashier lanes.",
                    'priority': 'high'
                })
            
            # Check for underperforming sections
            underperforming = self.analytics_aggregator.identify_underperforming_sections()
            if underperforming:
                recommendations.append({
                    'type': 'layout',
                    'title': 'Low Traffic Sections',
                    'description': f"Sections {', '.join(underperforming)} have low traffic. Consider layout changes or promotions.",
                    'priority': 'medium'
                })
            
            # Check predictions for upcoming peak
            predictions = context.get('predictions', [])
            if predictions:
                next_hour_pred = predictions[0] if predictions else None
                if next_hour_pred and next_hour_pred['predicted_visitors'] > 30:
                    recommendations.append({
                        'type': 'staffing',
                        'title': 'Peak Hour Approaching',
                        'description': f"Expected {next_hour_pred['predicted_visitors']} visitors at {next_hour_pred['prediction_hour']}:00. Ensure adequate staffing.",
                        'priority': 'high'
                    })
            
            # Save recommendations to database
            for rec in recommendations:
                self.db_manager.insert_recommendation(
                    recommendation_type=rec['type'],
                    title=rec['title'],
                    description=rec['description'],
                    priority=rec['priority']
                )
            
            return recommendations
        
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    def query(
        self,
        user_query: str,
        language: str = "en",
        session_id: str = "default"
    ) -> Dict:
        """
        Process user query and return response
        
        Args:
            user_query: User's question or request
            language: Language code ('en' or 'ar')
            session_id: Session identifier for conversation history
        
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Get current context
            context_data = self.get_current_context()
            
            # Format context
            context_str = format_analytics_context(context_data)
            
            # Select system prompt based on language
            system_prompt = SYSTEM_PROMPT_AR if language == "ar" else SYSTEM_PROMPT_EN
            
            # Add context to system prompt
            full_system_prompt = f"{system_prompt}\n\n{context_str}"
            
            # Get conversation history
            history = self.conversation_history.get(session_id, [])
            
            # Get response from Groq
            response = self.groq_client.get_response(
                user_message=user_query,
                system_prompt=full_system_prompt,
                conversation_history=history[-10:]  # Keep last 10 messages
            )
            
            if response is None:
                response = "I apologize, but I'm having trouble processing your request right now. Please try again."
            
            # Update conversation history
            if session_id not in self.conversation_history:
                self.conversation_history[session_id] = []
            
            self.conversation_history[session_id].append({
                "role": "user",
                "content": user_query
            })
            self.conversation_history[session_id].append({
                "role": "assistant",
                "content": response
            })
            
            # Generate fresh recommendations
            recommendations = self.generate_recommendations()
            
            return {
                'response': response,
                'recommendations': recommendations,
                'context': context_data
            }
        
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                'response': "An error occurred while processing your request.",
                'recommendations': [],
                'context': {}
            }
    
    def get_summary(self, language: str = "en") -> str:
        """Get automated summary of current store status"""
        try:
            context = self.get_current_context()
            
            if language == "ar":
                query = "قدم ملخصاً شاملاً لحالة المتجر الحالية مع التوصيات الرئيسية"
            else:
                query = "Provide a comprehensive summary of the current store status with key recommendations"
            
            result = self.query(query, language=language, session_id="summary")
            return result['response']
        
        except Exception as e:
            logger.error(f"Error getting summary: {e}")
            return "Unable to generate summary at this time."
    
    def clear_history(self, session_id: str = "default"):
        """Clear conversation history for a session"""
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]
            logger.info(f"Cleared conversation history for session: {session_id}")
