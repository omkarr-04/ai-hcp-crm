"""
Database model for Interaction Logs.
Defines the interaction_logs table structure.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from datetime import datetime
from database.connection import Base


class InteractionLog(Base):
    """
    InteractionLog model representing healthcare professional interactions.
    Stores all interaction data including HCP details, discussion notes, 
    sentiment analysis, and follow-up actions.
    """
    __tablename__ = "interaction_logs"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # HCP Information
    hcp_name = Column(String(255), nullable=False, index=True)
    hcp_specialty = Column(String(255), nullable=True)
    hcp_location = Column(String(255), nullable=True)
    
    # Interaction Details
    interaction_type = Column(String(100), nullable=False)  # In-Person, Virtual, Phone, Email
    discussion_notes = Column(Text, nullable=True)
    
    # Topics and Materials
    topics_discussed = Column(Text, nullable=True)  # JSON string of topics
    materials_shared = Column(Text, nullable=True)  # JSON string of materials
    samples_distributed = Column(Text, nullable=True)  # JSON string of samples
    
    # Sentiment and Summary
    sentiment = Column(String(50), nullable=True)  # Positive, Neutral, Negative
    sentiment_score = Column(Float, nullable=True)  # 0-1 scale
    summary = Column(Text, nullable=True)
    
    # Follow-up
    follow_up = Column(Text, nullable=True)
    follow_up_date = Column(DateTime, nullable=True)
    follow_up_completed = Column(String(10), default="pending")
    
    # Attendees
    attendees = Column(Text, nullable=True)  # JSON string of attendees
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # User tracking
    created_by = Column(String(100), nullable=True)
    interaction_date = Column(DateTime, nullable=True)
    interaction_time = Column(String(20), nullable=True)

    def __repr__(self):
        return f"<InteractionLog(id={self.id}, hcp_name='{self.hcp_name}', type='{self.interaction_type}')>"
    
    def to_dict(self):
        """
        Convert model to dictionary for JSON serialization.
        """
        return {
            "id": self.id,
            "hcp_name": self.hcp_name,
            "hcp_specialty": self.hcp_specialty,
            "hcp_location": self.hcp_location,
            "interaction_type": self.interaction_type,
            "discussion_notes": self.discussion_notes,
            "topics_discussed": self.topics_discussed,
            "materials_shared": self.materials_shared,
            "samples_distributed": self.samples_distributed,
            "sentiment": self.sentiment,
            "sentiment_score": self.sentiment_score,
            "summary": self.summary,
            "follow_up": self.follow_up,
            "follow_up_date": self.follow_up_date.isoformat() if self.follow_up_date else None,
            "follow_up_completed": self.follow_up_completed,
            "attendees": self.attendees,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
            "interaction_date": self.interaction_date.isoformat() if self.interaction_date else None,
            "interaction_time": self.interaction_time,
        }