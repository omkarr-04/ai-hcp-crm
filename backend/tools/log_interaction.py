"""
Log Interaction Tool for LangGraph.
Handles saving new interaction records to the database.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import json

from models.interaction import InteractionLog
from schemas.interaction import InteractionCreate


class LogInteractionTool:
    """
    Tool for logging new healthcare professional interactions.
    Extracts entities from natural language and saves structured data.
    """
    
    name = "log_interaction"
    description = "Log a new interaction with a healthcare professional. Use when the user wants to record a new HCP visit or meeting."
    
    def __init__(self, db: Session):
        """
        Initialize the tool with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def execute(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the log interaction tool.
        
        Args:
            interaction_data: Structured interaction data from AI extraction
            
        Returns:
            Dictionary with success status and result
        """
        try:
            # Parse JSON fields if they're strings
            topics = interaction_data.get("topics_discussed")
            if isinstance(topics, str):
                interaction_data["topics_discussed"] = topics
            elif topics is None:
                interaction_data["topics_discussed"] = None
            else:
                interaction_data["topics_discussed"] = json.dumps(topics) if topics else None
            
            materials = interaction_data.get("materials_shared")
            if isinstance(materials, str):
                interaction_data["materials_shared"] = materials
            elif materials is None:
                interaction_data["materials_shared"] = None
            else:
                interaction_data["materials_shared"] = json.dumps(materials) if materials else None
            
            samples = interaction_data.get("samples_distributed")
            if isinstance(samples, str):
                interaction_data["samples_distributed"] = samples
            elif samples is None:
                interaction_data["samples_distributed"] = None
            else:
                interaction_data["samples_distributed"] = json.dumps(samples) if samples else None
            
            attendees = interaction_data.get("attendees")
            if isinstance(attendees, str):
                interaction_data["attendees"] = attendees
            elif attendees is None:
                interaction_data["attendees"] = None
            else:
                interaction_data["attendees"] = json.dumps(attendees) if attendees else None
            
            # Set default values
            interaction_data.setdefault("sentiment", "Neutral")
            interaction_data.setdefault("follow_up_completed", "pending")
            
            # Create interaction record
            interaction = InteractionLog(**interaction_data)
            self.db.add(interaction)
            self.db.commit()
            self.db.refresh(interaction)
            
            return {
                "success": True,
                "message": f"Interaction logged successfully for {interaction_data.get('hcp_name', 'HCP')}",
                "interaction_id": interaction.id,
                "data": interaction.to_dict()
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Failed to log interaction: {str(e)}",
                "error": str(e)
            }
    
    def extract_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract structured data from natural language text.
        
        Args:
            text: Natural language description
            
        Returns:
            Extracted structured data
        """
        from services.groq_service import get_groq_service
        
        service = get_groq_service()
        result = service.extract_interaction_data(text)
        
        if result.get("success"):
            return result.get("data", {})
        return {}


def create_log_interaction_tool(db: Session) -> LogInteractionTool:
    """
    Factory function to create LogInteractionTool instance.
    
    Args:
        db: SQLAlchemy database session
        
    Returns:
        LogInteractionTool instance
    """
    return LogInteractionTool(db)