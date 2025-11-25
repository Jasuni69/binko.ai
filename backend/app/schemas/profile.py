from pydantic import BaseModel
from typing import Optional


class UserProfile(BaseModel):
    # Skills
    technical_skills: list[str] = []  # python, react, aws
    non_technical_skills: list[str] = []  # marketing, sales, writing
    experience_level: str = "beginner"  # beginner, intermediate, experienced

    # Preferences
    preferred_niches: list[str] = []  # fintech, health, education
    preferred_types: list[str] = []  # saas, service, content

    # Constraints
    hours_per_week: Optional[int] = None
    budget: Optional[str] = None  # free, <$100, <$1000, >$1000

    # Goals
    income_goal: Optional[str] = None  # side_income, replace_job, scale_big
    timeline: Optional[str] = None  # asap, 3_months, 6_months

    # Context
    interests: Optional[str] = None
    background: Optional[str] = None
