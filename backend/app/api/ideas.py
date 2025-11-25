from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.models.idea import Idea
from app.schemas.idea import IdeaCreate, IdeaResponse, IdeaList
from app.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("", response_model=IdeaList)
def list_ideas(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Max records to return"),
    niche: Optional[str] = None,
    difficulty: Optional[str] = None,
    idea_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List ideas with optional filters."""
    try:
        query = db.query(Idea)

        if niche:
            query = query.filter(Idea.niche == niche)
        if difficulty:
            query = query.filter(Idea.difficulty == difficulty)
        if idea_type:
            query = query.filter(Idea.idea_type == idea_type)

        total = query.count()
        ideas = query.offset(skip).limit(limit).all()

        logger.info(f"Listed {len(ideas)} ideas (total: {total})")
        return IdeaList(ideas=ideas, total=total)
    
    except SQLAlchemyError as e:
        logger.error(f"Database error listing ideas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database error"
        )


@router.get("/{idea_id}", response_model=IdeaResponse)
def get_idea(idea_id: UUID, db: Session = Depends(get_db)):
    """Get single idea by ID."""
    try:
        idea = db.query(Idea).filter(Idea.id == idea_id).first()
        if not idea:
            logger.warning(f"Idea not found: {idea_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Idea {idea_id} not found"
            )
        
        logger.info(f"Retrieved idea: {idea_id}")
        return idea
    
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error getting idea {idea_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database error"
        )


@router.post("", response_model=IdeaResponse, status_code=status.HTTP_201_CREATED)
def create_idea(idea: IdeaCreate, db: Session = Depends(get_db)):
    """Create new idea."""
    try:
        db_idea = Idea(**idea.model_dump())
        db.add(db_idea)
        db.commit()
        db.refresh(db_idea)
        
        logger.info(f"Created idea: {db_idea.id} - {db_idea.title}")
        return db_idea
    
    except IntegrityError as e:
        logger.error(f"Integrity error creating idea: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Idea already exists or invalid data"
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error creating idea: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database error"
        )


@router.post("/bulk", response_model=dict, status_code=status.HTTP_201_CREATED)
def bulk_create_ideas(
    ideas: list[IdeaCreate] = Query(..., max_length=100),
    db: Session = Depends(get_db)
):
    """Bulk create ideas. Max 100 at a time."""
    if len(ideas) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No ideas provided"
        )
    
    if len(ideas) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 100 ideas per bulk request"
        )
    
    try:
        db_ideas = [Idea(**idea.model_dump()) for idea in ideas]
        db.add_all(db_ideas)
        db.commit()
        
        logger.info(f"Bulk created {len(db_ideas)} ideas")
        return {"created": len(db_ideas)}
    
    except IntegrityError as e:
        logger.error(f"Integrity error in bulk create: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate or invalid ideas in batch"
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error in bulk create: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database error"
        )


@router.delete("/{idea_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_idea(idea_id: UUID, db: Session = Depends(get_db)):
    """Delete idea by ID."""
    try:
        idea = db.query(Idea).filter(Idea.id == idea_id).first()
        if not idea:
            logger.warning(f"Idea not found for deletion: {idea_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Idea {idea_id} not found"
            )
        
        db.delete(idea)
        db.commit()
        
        logger.info(f"Deleted idea: {idea_id}")
        return None
    
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error deleting idea {idea_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database error"
        )
