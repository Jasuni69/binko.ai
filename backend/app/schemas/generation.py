from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class GenerationRequest(BaseModel):
    profile: "UserProfile"
    num_ideas: int = 3

    class Config:
        from_attributes = True


class GeneratedIdea(BaseModel):
    title: str
    description: str
    why_good_fit: str
    first_steps: list[str]
    tech_recommendations: list[str]
    source_idea_ids: list[UUID] = []


class GenerationResponse(BaseModel):
    ideas: list[GeneratedIdea]
    profile_summary: str


from app.schemas.profile import UserProfile
GenerationRequest.model_rebuild()
