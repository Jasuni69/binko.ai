"""
Enhanced UserProfile schema with validation.
Replace profile.py with this when file locks clear.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal


class UserProfile(BaseModel):
    # Skills
    technical_skills: list[str] = Field(default=[], max_length=20, description="List of technical skills")
    non_technical_skills: list[str] = Field(default=[], max_length=20, description="List of non-technical skills")
    experience_level: Literal["beginner", "intermediate", "experienced"] = Field(default="beginner")

    # Preferences
    preferred_niches: list[str] = Field(default=[], max_length=10)
    preferred_types: list[str] = Field(default=[], max_length=10)

    # Constraints
    hours_per_week: Optional[int] = Field(default=None, ge=1, le=168, description="Hours available per week")
    budget: Optional[str] = Field(default=None, pattern="^(free|<\\$100|<\\$1000|>\\$1000)$")

    # Goals
    income_goal: Optional[str] = Field(default=None, pattern="^(side_income|replace_job|scale_big)$")
    timeline: Optional[str] = Field(default=None, pattern="^(asap|3_months|6_months|12_months)$")

    # Context
    interests: Optional[str] = Field(default=None, max_length=500)
    background: Optional[str] = Field(default=None, max_length=1000)

    @field_validator("technical_skills", "non_technical_skills", "preferred_niches", "preferred_types")
    @classmethod
    def validate_skill_lists(cls, v: list[str]) -> list[str]:
        """Ensure skill items are not empty strings."""
        return [item.strip() for item in v if item and item.strip()]
