"""
Summarize Interaction Tool for LangGraph.
Generates concise summaries of healthcare professional interactions.
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from models.interaction import InteractionLog
from services.groq_service import get_groq_service


class SummarizeInteractionTool:
    """
    Tool for generating concise visit summaries.
    Uses Groq LLM to create professional summaries.
    """
    
    name = "summarize_interaction"
    description = "Generate a concise summary of an interaction. Use when the user wants to see or regenerate a summary of a past interaction."
    
    def __init__(self, db: Session):
        """
        Initialize the tool with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def execute(self, interaction_id: int) -> Dict[str, Any]:
        """
        Execute the summarize interaction tool.
        
        Args:
            interaction_id: ID of the interaction to summarize
            
        Returns:
            Dictionary with success status and summary
        """
        try:
            # Find the interaction
            interaction = self.db.query(InteractionLog).filter(
                InteractionLog.id == interaction_id
            ).first()
            
            if not interaction:
                return {
                    "success": False,
                    "message": f"Interaction with ID {interaction_id} not found",
                    "error": "Not found"
                }
            
            # Use Groq service to generate summary
            service = get_groq_service()
            
            interaction_data = {
                "hcp_name": interaction.hcp_name,
                "interaction_type": interaction.interaction_type,
                "discussion_notes": interaction.discussion_notes,
                "topics_discussed": interaction.topics_discussed,
                "sentiment": interaction.sentiment,
                "follow_up": interaction.follow_up
            }
            
            summary = service.generate_summary(interaction_data)
            
            # Update the interaction with new summary
            interaction.summary = summary
            self.db.commit()
            
            return {
                "success": True,
                "message": "Summary generated successfully",
                "interaction_id": interaction_id,
                "summary": summary,
                "data": interaction.to_dict()
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Failed to generate summary: {str(e)}",
                "error": str(e)
            }
    
    def summarize_from_data(self, interaction_data: Dict[str, Any]) -> str:
        """
        Generate summary from raw interaction data.
        
        Args:
            interaction_data: Dictionary of interaction fields
            
        Returns:
            Generated summary string
        """
        service = get_groq_service()
        return service.generate_summary(interaction_data)


def create_summarize_interaction_tool(db: Session) -> SummarizeInteractionTool:
    """
    Factory function to create SummarizeInteractionTool instance.
    
    Args:
        db: SQLAlchemy database session
        
    Returns:
        SummarizeInteractionTool instance
    """
    return SummarizeInteractionTool(db)