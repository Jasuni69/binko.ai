from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.models.idea import Idea
from app.schemas.idea import IdeaCreate, IdeaResponse, IdeaList

router = APIRouter()


@router.get("", response_model=IdeaList)
def list_ideas(
    skip: int = 0,
    limit: int = 50,
    niche: Optional[str] = None,
    difficulty: Optional[str] = None,
    idea_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Idea)

    if niche:
        query = query.filter(Idea.niche == niche)
    if difficulty:
        query = query.filter(Idea.difficulty == difficulty)
    if idea_type:
        query = query.filter(Idea.idea_type == idea_type)

    total = query.count()
    ideas = query.offset(skip).limit(limit).all()

    return IdeaList(ideas=ideas, total=total)


@router.get("/{idea_id}", response_model=IdeaResponse)
def get_idea(idea_id: UUID, db: Session = Depends(get_db)):
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    return idea


@router.post("", response_model=IdeaResponse)
def create_idea(idea: IdeaCreate, db: Session = Depends(get_db)):
    db_idea = Idea(**idea.model_dump())
    db.add(db_idea)
    db.commit()
    db.refresh(db_idea)
    return db_idea


@router.post("/bulk", response_model=dict)
def bulk_create_ideas(ideas: list[IdeaCreate], db: Session = Depends(get_db)):
    db_ideas = [Idea(**idea.model_dump()) for idea in ideas]
    db.add_all(db_ideas)
    db.commit()
    return {"created": len(db_ideas)}


@router.delete("/{idea_id}")
def delete_idea(idea_id: UUID, db: Session = Depends(get_db)):
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    db.delete(idea)
    db.commit()
    return {"deleted": True}
