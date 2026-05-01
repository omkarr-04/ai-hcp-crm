"""
API routes for Interaction management.
Provides REST endpoints for CRUD operations on interactions.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database.connection import get_db
from models.interaction import InteractionLog
from schemas.interaction import (
    InteractionCreate,
    InteractionUpdate,
    InteractionResponse,
    InteractionListResponse,
    AIChatRequest,
    AIChatResponse
)
from agents.crm_agent import process_chat_message

# Create router
router = APIRouter(prefix="/api", tags=["Interactions"])


@router.post("/interaction", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED)
def create_interaction(
    interaction: InteractionCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new interaction log.
    
    Args:
        interaction: Interaction data from request
        db: Database session
        
    Returns:
        Created interaction record
    """
    try:
        db_interaction = InteractionLog(**interaction.dict())
        db.add(db_interaction)
        db.commit()
        db.refresh(db_interaction)
        return db_interaction
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create interaction: {str(e)}"
        )


@router.get("/interaction", response_model=InteractionListResponse)
def get_interactions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    hcp_name: Optional[str] = Query(None, description="Filter by HCP name"),
    sentiment: Optional[str] = Query(None, description="Filter by sentiment"),
    interaction_type: Optional[str] = Query(None, description="Filter by interaction type"),
    db: Session = Depends(get_db)
):
    """
    Get all interactions with optional filtering and pagination.
    
    Args:
        page: Page number
        page_size: Items per page
        hcp_name: Optional HCP name filter
        sentiment: Optional sentiment filter
        interaction_type: Optional interaction type filter
        db: Database session
        
    Returns:
        Paginated list of interactions
    """
    query = db.query(InteractionLog)
    
    # Apply filters
    if hcp_name:
        query = query.filter(InteractionLog.hcp_name.ilike(f"%{hcp_name}%"))
    if sentiment:
        query = query.filter(InteractionLog.sentiment == sentiment)
    if interaction_type:
        query = query.filter(InteractionLog.interaction_type == interaction_type)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    interactions = query.order_by(InteractionLog.created_at.desc()).offset(offset).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": interactions
    }


@router.get("/interaction/{interaction_id}", response_model=InteractionResponse)
def get_interaction(
    interaction_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific interaction by ID.
    
    Args:
        interaction_id: ID of the interaction
        db: Database session
        
    Returns:
        Interaction record
        
    Raises:
        HTTPException: If interaction not found
    """
    interaction = db.query(InteractionLog).filter(InteractionLog.id == interaction_id).first()
    
    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interaction with ID {interaction_id} not found"
        )
    
    return interaction


@router.put("/interaction/{interaction_id}", response_model=InteractionResponse)
def update_interaction(
    interaction_id: int,
    interaction_update: InteractionUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing interaction.
    
    Args:
        interaction_id: ID of the interaction to update
        interaction_update: Updated interaction data
        db: Database session
        
    Returns:
        Updated interaction record
        
    Raises:
        HTTPException: If interaction not found
    """
    db_interaction = db.query(InteractionLog).filter(InteractionLog.id == interaction_id).first()
    
    if not db_interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interaction with ID {interaction_id} not found"
        )
    
    # Update fields
    update_data = interaction_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_interaction, key, value)
    
    try:
        db.commit()
        db.refresh(db_interaction)
        return db_interaction
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update interaction: {str(e)}"
        )


@router.delete("/interaction/{interaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interaction(
    interaction_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete an interaction.
    
    Args:
        interaction_id: ID of the interaction to delete
        db: Database session
        
    Raises:
        HTTPException: If interaction not found
    """
    db_interaction = db.query(InteractionLog).filter(InteractionLog.id == interaction_id).first()
    
    if not db_interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interaction with ID {interaction_id} not found"
        )
    
    try:
        db.delete(db_interaction)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete interaction: {str(e)}"
        )


@router.post("/ai/chat", response_model=AIChatResponse)
def ai_chat(
    request: AIChatRequest,
    db: Session = Depends(get_db)
):
    """
    Process AI chat message using LangGraph agent.
    
    Args:
        request: Chat request with user message
        db: Database session
        
    Returns:
        AI response with extracted data and action
    """
    try:
        result = process_chat_message(
            db=db,
            user_message=request.message,
            context=request.context or {}
        )
        
        return {
            "response": result.get("response", ""),
            "extracted_data": result.get("extracted_data"),
            "action": result.get("action"),
            "interaction_id": result.get("interaction_id")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI chat processing failed: {str(e)}"
        )


@router.get("/stats/summary")
def get_stats_summary(
    db: Session = Depends(get_db)
):
    """
    Get summary statistics for the dashboard.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with statistics
    """
    try:
        total_interactions = db.query(InteractionLog).count()
        
        # Sentiment breakdown
        sentiments = db.query(InteractionLog.sentiment).all()
        sentiment_counts = {"Positive": 0, "Neutral": 0, "Negative": 0}
        for s in sentiments:
            if s.sentiment in sentiment_counts:
                sentiment_counts[s.sentiment] += 1
        
        # Interaction type breakdown
        interaction_types = db.query(InteractionLog.interaction_type).all()
        type_counts = {}
        for t in interaction_types:
            if t.interaction_type:
                type_counts[t.interaction_type] = type_counts.get(t.interaction_type, 0) + 1
        
        # Recent interactions
        recent = db.query(InteractionLog).order_by(
            InteractionLog.created_at.desc()
        ).limit(5).all()
        
        return {
            "total_interactions": total_interactions,
            "sentiment_breakdown": sentiment_counts,
            "interaction_type_breakdown": type_counts,
            "recent_interactions": [i.to_dict() for i in recent]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )