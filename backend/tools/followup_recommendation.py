"""
Follow-Up Recommendation Tool for LangGraph.
Suggests next actions based on interaction data.
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from models.interaction import InteractionLog
from services.groq_service import get_groq_service


class FollowUpRecommendationTool:
    """
    Tool for suggesting follow-up actions.
    Analyzes interaction data to recommend next steps.
    """
    
    name = "followup_recommendation"
    description = "Suggest follow-up actions for an interaction. Use when the user wants recommendations on what to do next with an HCP."
    
    def __init__(self, db: Session):
        """
        Initialize the tool with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def execute(self, interaction_id: int) -> Dict[str, Any]:
        """
        Execute the follow-up recommendation tool.
        
        Args:
            interaction_id: ID of the interaction to get recommendations for
            
        Returns:
            Dictionary with success status and recommendations
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
            
            # Use Groq service to generate recommendations
            service = get_groq_service()
            
            interaction_data = {
                "hcp_name": interaction.hcp_name,
                "interaction_type": interaction.interaction_type,
                "discussion_notes": interaction.discussion_notes,
                "topics_discussed": interaction.topics_discussed,
                "sentiment": interaction.sentiment,
                "follow_up": interaction.follow_up
            }
            
            recommendations = service.suggest_follow_up(interaction_data)
            
            return {
                "success": True,
                "message": "Recommendations generated successfully",
                "interaction_id": interaction_id,
                "recommendations": recommendations,
                "current_follow_up": interaction.follow_up
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to generate recommendations: {str(e)}",
                "error": str(e)
            }
    
    def get_default_recommendations(self, sentiment: str, topics: Optional[str] = None) -> List[str]:
        """
        Get default recommendations based on sentiment and topics.
        
        Args:
            sentiment: Interaction sentiment
            topics: Topics discussed
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        if sentiment == "Positive":
            recommendations.extend([
                "Schedule follow-up visit in 2-4 weeks",
                "Send thank you email with additional product information",
                "Share relevant clinical trial data"
            ])
        elif sentiment == "Neutral":
            recommendations.extend([
                "Schedule follow-up call to address questions",
                "Provide additional educational materials",
                "Invite to product webinar or conference"
            ])
        else:  # Negative
            recommendations.extend([
                "Follow up with customer service feedback",
                "Schedule check-in call after appropriate cooling period",
                "Provide alternative product options"
            ])
        
        return recommendations


def create_followup_recommendation_tool(db: Session) -> FollowUpRecommendationTool:
    """
    Factory function to create FollowUpRecommendationTool instance.
    
    Args:
        db: SQLAlchemy database session
        
    Returns:
        FollowUpRecommendationTool instance
    """
    return FollowUpRecommendationTool(db)