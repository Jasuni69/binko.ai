import json
from sqlalchemy.orm import Session
from openai import AsyncOpenAI

from app.config import get_settings
from app.models.idea import Idea
from app.schemas.profile import UserProfile
from app.schemas.generation import GenerationResponse, GeneratedIdea

settings = get_settings()
client = AsyncOpenAI(api_key=settings.openai_api_key)


async def generate_ideas(
    profile: UserProfile, num_ideas: int, db: Session
) -> GenerationResponse:
    # Get relevant ideas from database
    source_ideas = get_matching_ideas(profile, db)

    # Build prompt
    prompt = build_generation_prompt(profile, source_ideas, num_ideas)

    # Call OpenAI
    response = await client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.8,
    )

    # Parse response
    result = json.loads(response.choices[0].message.content)

    generated = [
        GeneratedIdea(
            title=idea["title"],
            description=idea["description"],
            why_good_fit=idea["why_good_fit"],
            first_steps=idea["first_steps"],
            tech_recommendations=idea["tech_recommendations"],
            source_idea_ids=[],
        )
        for idea in result["ideas"]
    ]

    return GenerationResponse(
        ideas=generated,
        profile_summary=result.get("profile_summary", ""),
    )


def get_matching_ideas(profile: UserProfile, db: Session, limit: int = 15) -> list[Idea]:
    """Get ideas that match user profile. Simple filtering for MVP."""
    query = db.query(Idea)

    # Filter by difficulty based on experience
    if profile.experience_level == "beginner":
        query = query.filter(Idea.difficulty.in_(["beginner", None]))
    elif profile.experience_level == "intermediate":
        query = query.filter(Idea.difficulty.in_(["beginner", "intermediate", None]))

    # Filter by preferred niches if specified
    if profile.preferred_niches:
        query = query.filter(Idea.niche.in_(profile.preferred_niches))

    # Filter by preferred types if specified
    if profile.preferred_types:
        query = query.filter(Idea.idea_type.in_(profile.preferred_types))

    return query.limit(limit).all()


def build_generation_prompt(
    profile: UserProfile, ideas: list[Idea], num_ideas: int
) -> str:
    # Format profile
    profile_str = f"""
USER PROFILE:
- Technical Skills: {', '.join(profile.technical_skills) or 'None specified'}
- Other Skills: {', '.join(profile.non_technical_skills) or 'None specified'}
- Experience Level: {profile.experience_level}
- Preferred Niches: {', '.join(profile.preferred_niches) or 'Open to any'}
- Preferred Types: {', '.join(profile.preferred_types) or 'Open to any'}
- Hours/Week Available: {profile.hours_per_week or 'Flexible'}
- Budget: {profile.budget or 'Not specified'}
- Income Goal: {profile.income_goal or 'Not specified'}
- Timeline: {profile.timeline or 'Flexible'}
- Interests: {profile.interests or 'Not specified'}
- Background: {profile.background or 'Not specified'}
"""

    # Format source ideas
    ideas_str = "\n\n".join(
        [
            f"""IDEA {i+1}: {idea.title}
Summary: {idea.summary}
Type: {idea.idea_type} | Model: {idea.business_model}
Skills: {', '.join(idea.skills or [])}
Difficulty: {idea.difficulty}
Niche: {idea.niche}"""
            for i, idea in enumerate(ideas)
        ]
    )

    return f"""{profile_str}

INSPIRATION IDEAS FROM SUCCESSFUL CREATORS:
{ideas_str if ideas else 'No specific inspiration ideas available.'}

Generate {num_ideas} NEW, ORIGINAL project ideas for this user.
Each idea should be unique and tailored to their specific profile.
If no inspiration ideas provided, create ideas based purely on user profile."""


SYSTEM_PROMPT = """You are a startup idea generator. Create NEW, ORIGINAL project ideas for users based on their profile and patterns from successful ideas.

Your ideas should:
1. Match the user's skill set (or stretch slightly)
2. Fit their budget and time constraints
3. Align with their interests and goals
4. Be actionable with clear first steps
5. NOT be copies of inspiration ideas - synthesize new angles

Return JSON in this exact format:
{
  "profile_summary": "Brief summary of what makes this user unique",
  "ideas": [
    {
      "title": "Catchy project name",
      "description": "3-4 sentences explaining the idea",
      "why_good_fit": "Why this matches THIS user specifically",
      "first_steps": ["Step 1", "Step 2", "Step 3"],
      "tech_recommendations": ["Tool or tech 1", "Tool 2"]
    }
  ]
}"""
