"""
Groq API client for LLM interactions
"""
from groq import Groq
from typing import List, Dict, Optional
import logging
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GroqClient:
    """Client for interacting with Groq API"""
    
    def __init__(self):
        """Initialize Groq client"""
        try:
            self.client = Groq(api_key=settings.GROQ_API_KEY)
            self.model = settings.GROQ_MODEL
            logger.info(f"Groq client initialized with model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            raise
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> Optional[str]:
        """
        Get chat completion from Groq
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
        
        Returns:
            Response text or None if error
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Error in Groq chat completion: {e}")
            return None
    
    def get_response(
        self,
        user_message: str,
        system_prompt: str = None,
        conversation_history: List[Dict] = None
    ) -> Optional[str]:
        """
        Get a response from the chatbot
        
        Args:
            user_message: User's message
            system_prompt: System prompt to set context
            conversation_history: Previous conversation messages
        
        Returns:
            Chatbot response
        """
        messages = []
        
        # Add system prompt
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return self.chat_completion(messages)
