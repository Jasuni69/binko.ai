"""
Enhanced generation schemas with validation.
Replace generation.py with this when file locks clear.
"""
from pydantic import BaseModel, Field
from uuid import UUID


class GenerationRequest(BaseModel):
    profile: "UserProfile"
    num_ideas: int = Field(default=3, ge=1, le=10, description="Number of ideas to generate")

    class Config:
        from_attributes = True


class GeneratedIdea(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10, max_length=1000)
    why_good_fit: str = Field(..., min_length=10, max_length=500)
    first_steps: list[str] = Field(..., min_length=1, max_length=10)
    tech_recommendations: list[str] = Field(..., max_length=10)
    source_idea_ids: list[UUID] = Field(default=[])


class GenerationResponse(BaseModel):
    ideas: list[GeneratedIdea] = Field(..., min_length=1)
    profile_summary: str = Field(..., max_length=500)


from app.schemas.profile import UserProfile
GenerationRequest.model_rebuild()
