"""
HCP History Tool for LangGraph.
Fetches previous interaction history for healthcare professionals.
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.interaction import InteractionLog
from services.groq_service import get_groq_service


class HCPHistoryTool:
    """
    Tool for fetching HCP interaction history.
    Shows trends and previous meetings.
    """
    
    name = "hcp_history"
    description = "Get interaction history for a healthcare professional. Use when the user wants to see past interactions with a specific HCP."
    
    def __init__(self, db: Session):
        """
        Initialize the tool with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def execute(self, hcp_name: str, limit: int = 10) -> Dict[str, Any]:
        """
        Execute the HCP history tool.
        
        Args:
            hcp_name: Name of the healthcare professional
            limit: Maximum number of interactions to return
            
        Returns:
            Dictionary with success status and history data
        """
        try:
            # Find interactions for the HCP
            interactions = self.db.query(InteractionLog).filter(
                InteractionLog.hcp_name.ilike(f"%{hcp_name}%")
            ).order_by(desc(InteractionLog.created_at)).limit(limit).all()
            
            if not interactions:
                return {
                    "success": True,
                    "message": f"No interaction history found for {hcp_name}",
                    "hcp_name": hcp_name,
                    "interactions": [],
                    "total_interactions": 0
                }
            
            # Convert to dictionaries
            interaction_list = [i.to_dict() for i in interactions]
            
            # Calculate summary statistics
            sentiments = [i.sentiment for i in interactions if i.sentiment]
            sentiment_counts = {}
            for s in sentiments:
                sentiment_counts[s] = sentiment_counts.get(s, 0) + 1
            
            # Get unique interaction types
            interaction_types = list(set([i.interaction_type for i in interactions if i.interaction_type]))
            
            # Generate AI summary if there are interactions
            summary = None
            if len(interactions) > 0:
                service = get_groq_service()
                summary = service.get_hcp_history_summary(interaction_list)
            
            return {
                "success": True,
                "message": f"Found {len(interactions)} interactions for {hcp_name}",
                "hcp_name": hcp_name,
                "interactions": interaction_list,
                "total_interactions": len(interactions),
                "sentiment_breakdown": sentiment_counts,
                "interaction_types": interaction_types,
                "ai_summary": summary
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to fetch HCP history: {str(e)}",
                "error": str(e)
            }
    
    def get_recent_interactions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent interactions across all HCPs.
        
        Args:
            limit: Maximum number of interactions to return
            
        Returns:
            List of recent interactions
        """
        interactions = self.db.query(InteractionLog).order_by(
            desc(InteractionLog.created_at)
        ).limit(limit).all()
        
        return [i.to_dict() for i in interactions]
    
    def get_trends(self, hcp_name: str) -> Dict[str, Any]:
        """
        Get interaction trends for an HCP.
        
        Args:
            hcp_name: Name of the healthcare professional
            
        Returns:
            Dictionary with trend data
        """
        interactions = self.db.query(InteractionLog).filter(
            InteractionLog.hcp_name.ilike(f"%{hcp_name}%")
        ).order_by(InteractionLog.created_at).all()
        
        if not interactions:
            return {"success": True, "trends": None, "message": "No data for trends"}
        
        # Calculate trends
        total = len(interactions)
        positive = sum(1 for i in interactions if i.sentiment == "Positive")
        neutral = sum(1 for i in interactions if i.sentiment == "Neutral")
        negative = sum(1 for i in interactions if i.sentiment == "Negative")
        
        # Calculate average time between interactions
        if len(interactions) > 1:
            dates = [i.created_at for i in interactions if i.created_at]
            dates.sort()
            if len(dates) > 1:
                from datetime import timedelta
                total_days = (dates[-1] - dates[0]).days
                avg_days = total_days / (len(dates) - 1)
            else:
                avg_days = None
        else:
            avg_days = None
        
        return {
            "success": True,
            "trends": {
                "total_interactions": total,
                "positive_ratio": positive / total if total > 0 else 0,
                "neutral_ratio": neutral / total if total > 0 else 0,
                "negative_ratio": negative / total if total > 0 else 0,
                "average_days_between": avg_days,
                "last_interaction": interactions[-1].to_dict() if interactions else None
            }
        }


def create_hcp_history_tool(db: Session) -> HCPHistoryTool:
    """
    Factory function to create HCPHistoryTool instance.
    
    Args:
        db: SQLAlchemy database session
        
    Returns:
        HCPHistoryTool instance
    """
    return HCPHistoryTool(db)