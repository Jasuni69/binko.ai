from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class IdeaCreate(BaseModel):
    title: str
    summary: str
    description: Optional[str] = None
    idea_type: Optional[str] = None
    business_model: Optional[str] = None
    monetization: Optional[str] = None
    skills: Optional[list[str]] = []
    tech_stack: Optional[list[str]] = []
    difficulty: Optional[str] = None
    time_to_mvp: Optional[str] = None
    startup_cost: Optional[str] = None
    target_audience: Optional[str] = None
    niche: Optional[str] = None
    competition: Optional[str] = None
    key_features: Optional[list[str]] = []
    success_factors: Optional[list[str]] = []
    challenges: Optional[list[str]] = []
    source_video_id: Optional[str] = None
    source_channel: Optional[str] = None
    confidence: Optional[float] = None


class IdeaResponse(IdeaCreate):
    id: UUID

    class Config:
        from_attributes = True


class IdeaList(BaseModel):
    ideas: list[IdeaResponse]
    total: int
