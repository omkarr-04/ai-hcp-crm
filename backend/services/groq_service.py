"""
Groq LLM Service for AI-HCP CRM.
Handles communication with Groq API for natural language processing.
"""

import os
import json
from typing import Optional, Dict, Any, List
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Groq API key from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Model configuration
MODEL_NAME = "gemma2-9b-it"
TEMPERATURE = 0.7
MAX_TOKENS = 2048


class GroqService:
    """
    Service class for interacting with Groq LLM API.
    Provides methods for text generation, entity extraction,
    and conversational AI capabilities.
    """
    
    def __init__(self):
        """Initialize Groq service with API client."""
        self.client = client
        self.model = MODEL_NAME
        self.temperature = TEMPERATURE
        self.max_tokens = MAX_TOKENS
    
    def _create_messages(self, system_prompt: str, user_message: str) -> List[Dict[str, str]]:
        """
        Create message format for Groq API.
        
        Args:
            system_prompt: System instructions
            user_message: User input message
            
        Returns:
            List of message dictionaries
        """
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    
    def generate_response(
        self, 
        system_prompt: str, 
        user_message: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate response from Groq LLM.
        
        Args:
            system_prompt: System instructions
            user_message: User input message
            temperature: Override default temperature
            max_tokens: Override default max tokens
            
        Returns:
            Dictionary with response and metadata
        """
        if not self.client:
            return {
                "success": False,
                "error": "Groq client not initialized. Check GROQ_API_KEY.",
                "content": ""
            }
        
        try:
            messages = self._create_messages(system_prompt, user_message)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            return {
                "success": True,
                "content": response.choices[0].message.content,
                "usage": response.usage,
                "model": response.model
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": ""
            }
    
    def extract_interaction_data(self, user_message: str) -> Dict[str, Any]:
        """
        Extract structured CRM data from natural language input.
        
        Args:
            user_message: Natural language description of interaction
            
        Returns:
            Dictionary with extracted structured data
        """
        system_prompt = """You are an AI CRM assistant for a healthcare pharmaceutical company.
Your task is to extract structured information from natural language descriptions of HCP interactions.

Extract the following fields from the user message:
- hcp_name: Name of the healthcare professional
- interaction_type: Type of interaction (In-Person Visit, Virtual Meeting, Phone Call, Email)
- discussion_notes: Key discussion points
- topics_discussed: List of topics discussed (as JSON array)
- materials_shared: List of materials shared (as JSON array)
- samples_distributed: List of samples given (as JSON array)
- sentiment: Sentiment of interaction (Positive, Neutral, Negative)
- follow_up: Recommended follow-up actions

Return ONLY a valid JSON object with these fields. If a field is not mentioned, use null.
Example format:
{
  "hcp_name": "Dr. John Smith",
  "interaction_type": "In-Person Visit",
  "discussion_notes": "Discussed new diabetes medication",
  "topics_discussed": ["Diabetes treatment", "Clinical trials"],
  "materials_shared": ["Product brochure"],
  "samples_distributed": null,
  "sentiment": "Positive",
  "follow_up": "Schedule follow-up visit next week"
}"""
        
        result = self.generate_response(system_prompt, user_message)
        
        if result["success"]:
            try:
                data = json.loads(result["content"])
                return {"success": True, "data": data}
            except json.JSONDecodeError:
                return {"success": False, "error": "Failed to parse JSON response"}
        
        return result
    
    def generate_summary(self, interaction_data: Dict[str, Any]) -> str:
        """
        Generate a concise summary of an interaction.
        
        Args:
            interaction_data: Structured interaction data
            
        Returns:
            Generated summary string
        """
        system_prompt = """You are an AI CRM assistant. Generate a concise, professional summary 
of a healthcare professional interaction based on the provided data. The summary should be 
2-3 sentences and capture the key points."""
        
        user_message = f"""Generate a summary for this interaction:
HCP Name: {interaction_data.get('hcp_name', 'N/A')}
Type: {interaction_data.get('interaction_type', 'N/A')}
Notes: {interaction_data.get('discussion_notes', 'N/A')}
Topics: {interaction_data.get('topics_discussed', 'N/A')}
Sentiment: {interaction_data.get('sentiment', 'N/A')}"""
        
        result = self.generate_response(system_prompt, user_message, temperature=0.5)
        
        if result["success"]:
            return result["content"]
        return "Summary generation failed."
    
    def suggest_follow_up(self, interaction_data: Dict[str, Any]) -> str:
        """
        Suggest follow-up actions based on interaction data.
        
        Args:
            interaction_data: Structured interaction data
            
        Returns:
            Follow-up recommendations
        """
        system_prompt = """You are an AI CRM assistant. Based on the interaction data provided,
suggest appropriate follow-up actions for a pharmaceutical sales representative.
Consider the sentiment, topics discussed, and HCP preferences.
Return a concise list of 2-3 actionable follow-up items."""
        
        user_message = f"""Suggest follow-up actions for:
HCP: {interaction_data.get('hcp_name', 'N/A')}
Topics: {interaction_data.get('topics_discussed', 'N/A')}
Sentiment: {interaction_data.get('sentiment', 'N/A')}
Notes: {interaction_data.get('discussion_notes', 'N/A')}"""
        
        result = self.generate_response(system_prompt, user_message, temperature=0.6)
        
        if result["success"]:
            return result["content"]
        return "Follow-up recommendation failed."
    
    def get_hcp_history_summary(self, interactions: List[Dict[str, Any]]) -> str:
        """
        Generate a summary of HCP interaction history.
        
        Args:
            interactions: List of past interaction data
            
        Returns:
            History summary
        """
        system_prompt = """You are an AI CRM assistant. Analyze the interaction history 
with a healthcare professional and provide a brief summary of trends and key points."""
        
        user_message = f"""Summarize this HCP's interaction history:
{json.dumps(interactions, indent=2)}"""
        
        result = self.generate_response(system_prompt, user_message, temperature=0.5)
        
        if result["success"]:
            return result["content"]
        return "History summary failed."


# Create singleton instance
groq_service = GroqService()


def get_groq_service() -> GroqService:
    """
    Get the Groq service singleton.
    
    Returns:
        GroqService instance
    """
    return groq_service