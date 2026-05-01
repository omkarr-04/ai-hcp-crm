"""
Pydantic schemas for Interaction API.
Defines request and response models for validation.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class InteractionBase(BaseModel):
    """
    Base schema with common interaction fields.
    """
    hcp_name: str = Field(..., description="Name of Healthcare Professional")
    hcp_specialty: Optional[str] = Field(None, description="HCP Specialty")
    hcp_location: Optional[str] = Field(None, description="HCP Location")
    interaction_type: str = Field(..., description="Type of interaction")
    discussion_notes: Optional[str] = Field(None, description="Notes from discussion")
    topics_discussed: Optional[str] = Field(None, description="JSON string of topics")
    materials_shared: Optional[str] = Field(None, description="JSON string of materials")
    samples_distributed: Optional[str] = Field(None, description="JSON string of samples")
    sentiment: Optional[str] = Field(None, description="Sentiment: Positive, Neutral, Negative")
    sentiment_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Sentiment score 0-1")
    summary: Optional[str] = Field(None, description="AI-generated summary")
    follow_up: Optional[str] = Field(None, description="Follow-up actions")
    follow_up_date: Optional[datetime] = Field(None, description="Follow-up date")
    attendees: Optional[str] = Field(None, description="JSON string of attendees")
    created_by: Optional[str] = Field(None, description="User who created the record")
    interaction_date: Optional[datetime] = Field(None, description="Date of interaction")
    interaction_time: Optional[str] = Field(None, description="Time of interaction")


class InteractionCreate(InteractionBase):
    """
    Schema for creating a new interaction.
    """
    pass


class InteractionUpdate(BaseModel):
    """
    Schema for updating an existing interaction.
    All fields are optional to allow partial updates.
    """
    hcp_name: Optional[str] = None
    hcp_specialty: Optional[str] = None
    hcp_location: Optional[str] = None
    interaction_type: Optional[str] = None
    discussion_notes: Optional[str] = None
    topics_discussed: Optional[str] = None
    materials_shared: Optional[str] = None
    samples_distributed: Optional[str] = None
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    summary: Optional[str] = None
    follow_up: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    follow_up_completed: Optional[str] = None
    attendees: Optional[str] = None
    interaction_date: Optional[datetime] = None
    interaction_time: Optional[str] = None


class InteractionResponse(InteractionBase):
    """
    Schema for interaction response.
    Includes all fields plus metadata.
    """
    id: int
    follow_up_completed: Optional[str] = "pending"
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InteractionListResponse(BaseModel):
    """
    Schema for paginated list of interactions.
    """
    total: int
    page: int
    page_size: int
    items: List[InteractionResponse]


class AIChatRequest(BaseModel):
    """
    Schema for AI chat request.
    """
    message: str = Field(..., description="User message in natural language")
    context: Optional[dict] = Field(None, description="Additional context for the AI")
    hcp_name: Optional[str] = Field(None, description="HCP name if provided")


class AIChatResponse(BaseModel):
    """
    Schema for AI chat response.
    """
    response: str = Field(..., description="AI response message")
    extracted_data: Optional[dict] = Field(None, description="Extracted structured data")
    action: Optional[str] = Field(None, description="Action performed: log, edit, summarize, etc.")
    interaction_id: Optional[int] = Field(None, description="Related interaction ID if any")


class ToolResult(BaseModel):
    """
    Schema for tool execution results.
    """
    tool_name: str
    success: bool
    result: Optional[dict] = None
    error: Optional[str] = None
    message: str