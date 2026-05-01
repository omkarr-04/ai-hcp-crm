"""
Edit Interaction Tool for LangGraph.
Handles updating existing interaction records.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from models.interaction import InteractionLog
import json


class EditInteractionTool:
    """
    Tool for editing existing healthcare professional interactions.
    Updates fields dynamically based on user input.
    """
    
    name = "edit_interaction"
    description = "Edit an existing interaction record. Requires interaction ID and the fields to update."
    
    def __init__(self, db: Session):
        """
        Initialize the tool with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def execute(self, interaction_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the edit interaction tool.
        
        Args:
            interaction_id: ID of the interaction to update
            update_data: Dictionary of fields to update
            
        Returns:
            Dictionary with success status and result
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
            
            # Update fields
            for key, value in update_data.items():
                if hasattr(interaction, key) and value is not None:
                    # Handle JSON fields
                    if key in ["topics_discussed", "materials_shared", "samples_distributed", "attendees"]:
                        if isinstance(value, list):
                            setattr(interaction, key, json.dumps(value))
                        elif isinstance(value, str):
                            setattr(interaction, key, value)
                    else:
                        setattr(interaction, key, value)
            
            # Update timestamp
            from datetime import datetime
            interaction.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(interaction)
            
            return {
                "success": True,
                "message": f"Interaction {interaction_id} updated successfully",
                "interaction_id": interaction_id,
                "data": interaction.to_dict()
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Failed to update interaction: {str(e)}",
                "error": str(e)
            }
    
    def find_by_hcp_name(self, hcp_name: str) -> list:
        """
        Find interactions by HCP name.
        
        Args:
            hcp_name: Name of the healthcare professional
            
        Returns:
            List of matching interactions
        """
        interactions = self.db.query(InteractionLog).filter(
            InteractionLog.hcp_name.ilike(f"%{hcp_name}%")
        ).order_by(InteractionLog.created_at.desc()).all()
        
        return [i.to_dict() for i in interactions]


def create_edit_interaction_tool(db: Session) -> EditInteractionTool:
    """
    Factory function to create EditInteractionTool instance.
    
    Args:
        db: SQLAlchemy database session
        
    Returns:
        EditInteractionTool instance
    """
    return EditInteractionTool(db)