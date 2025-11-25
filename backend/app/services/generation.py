import json
import logging
from typing import Optional
from sqlalchemy.orm import Session
from openai import AsyncOpenAI

from app.config import get_settings
from app.models.idea import Idea
from app.schemas.profile import UserProfile
from app.schemas.generation import GenerationResponse, GeneratedIdea

logger = logging.getLogger(__name__)
settings = get_settings()
client = AsyncOpenAI(api_key=settings.openai_api_key)

MAX_RETRIES = 3
SKILL_MATCH_THRESHOLD = 0.5


async def generate_ideas(
    profile: UserProfile, num_ideas: int, db: Session
) -> GenerationResponse:
    """Generate ideas with validation and fallback."""

    for attempt in range(MAX_RETRIES):
        try:
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

            # Validate schema
            if not validate_response_schema(result):
                logger.warning(f"Attempt {attempt + 1}: Invalid schema in AI response")
                continue

            # Build ideas
            generated = []
            for idea in result["ideas"]:
                idea_obj = GeneratedIdea(
                    title=idea["title"],
                    description=idea["description"],
                    why_good_fit=idea["why_good_fit"],
                    first_steps=idea["first_steps"],
                    tech_recommendations=idea["tech_recommendations"],
                    source_idea_ids=[],
                )

                # Validate each idea
                validation_result = validate_idea(idea_obj, profile)
                if not validation_result["valid"]:
                    logger.warning(
                        f"Attempt {attempt + 1}: Idea '{idea['title']}' failed validation: "
                        f"{', '.join(validation_result['reasons'])}"
                    )
                    # Skip this idea but keep others
                    continue

                generated.append(idea_obj)

            # Check if we got enough valid ideas
            if len(generated) >= num_ideas:
                return GenerationResponse(
                    ideas=generated[:num_ideas],
                    profile_summary=result.get("profile_summary", ""),
                )
            else:
                logger.warning(
                    f"Attempt {attempt + 1}: Only {len(generated)}/{num_ideas} ideas passed validation"
                )

        except json.JSONDecodeError as e:
            logger.error(f"Attempt {attempt + 1}: JSON parse error: {e}")
        except Exception as e:
            logger.error(f"Attempt {attempt + 1}: Generation error: {e}")

    # All retries failed - return safe fallback ideas
    logger.error(f"All {MAX_RETRIES} attempts failed. Returning fallback ideas.")
    return get_fallback_ideas(profile, num_ideas, db)


def validate_idea(idea: GeneratedIdea, profile: UserProfile) -> dict:
    """Validate generated idea against user profile."""
    reasons = []

    # 1. Skill validation
    if not validate_skill_match(idea.tech_recommendations, profile.technical_skills):
        reasons.append("Tech stack mismatch - less than 50% overlap with user skills")

    # 2. Budget validation
    if not validate_budget_match(idea.tech_recommendations, profile.budget):
        reasons.append("Suggests paid tools but user has free/low budget")

    # 3. Difficulty validation
    if not validate_difficulty_match(idea, profile.experience_level):
        reasons.append("Difficulty mismatch - too advanced for user level")

    return {
        "valid": len(reasons) == 0,
        "reasons": reasons
    }


def validate_skill_match(tech_recommendations: list[str], user_skills: list[str]) -> bool:
    """Check if tech recommendations overlap with user skills by at least 50%."""
    if not user_skills or not tech_recommendations:
        # If user has no skills listed, allow anything
        return len(user_skills) == 0

    # Normalize to lowercase for comparison
    user_skills_lower = {skill.lower() for skill in user_skills}
    tech_lower = {tech.lower() for tech in tech_recommendations}

    # Count matches
    matches = len(tech_lower.intersection(user_skills_lower))
    match_ratio = matches / len(tech_recommendations)

    return match_ratio >= SKILL_MATCH_THRESHOLD


def validate_budget_match(tech_recommendations: list[str], budget: Optional[str]) -> bool:
    """Check if tech recommendations fit budget constraints."""
    if not budget:
        return True

    budget_lower = budget.lower()

    # Define paid services/tools
    PAID_KEYWORDS = [
        "aws", "azure", "gcp", "heroku", "vercel pro", "netlify pro",
        "mongodb atlas", "planetscale", "supabase pro", "firebase blaze",
        "stripe", "openai api", "anthropic", "replicate",
        "cloudflare pro", "sendgrid paid", "twilio",
        "premium", "paid", "subscription", "enterprise"
    ]

    # Check if budget is free or very low
    if budget_lower in ["free", "$0", "no budget"]:
        for tech in tech_recommendations:
            tech_lower = tech.lower()
            if any(keyword in tech_lower for keyword in PAID_KEYWORDS):
                return False

    # For <$100 budget, allow some services but flag expensive ones
    if "<$100" in budget_lower or "under $100" in budget_lower or "< $100" in budget_lower:
        EXPENSIVE_KEYWORDS = [
            "aws", "azure", "gcp", "enterprise", "premium tier",
            "openai api", "anthropic"
        ]
        for tech in tech_recommendations:
            tech_lower = tech.lower()
            if any(keyword in tech_lower for keyword in EXPENSIVE_KEYWORDS):
                return False

    return True


def validate_difficulty_match(idea: GeneratedIdea, experience_level: str) -> bool:
    """Check if idea matches user experience level."""
    if experience_level == "beginner":
        # Beginners should not get complex frameworks or architectures
        ADVANCED_KEYWORDS = [
            "kubernetes", "docker compose", "microservices", "redis",
            "elasticsearch", "kafka", "graphql", "websockets",
            "nextjs", "remix", "svelte", "vue", "angular",
            "terraform", "ci/cd", "jenkins", "github actions"
        ]

        all_text = " ".join(idea.tech_recommendations).lower()
        all_text += " " + idea.description.lower()

        for keyword in ADVANCED_KEYWORDS:
            if keyword in all_text:
                return False

    return True


def validate_response_schema(response: dict) -> bool:
    """Validate AI response has required fields."""
    try:
        if "ideas" not in response:
            return False

        for idea in response["ideas"]:
            required = ["title", "description", "why_good_fit", "first_steps", "tech_recommendations"]
            if not all(field in idea for field in required):
                return False

            # Check types
            if not isinstance(idea["first_steps"], list):
                return False
            if not isinstance(idea["tech_recommendations"], list):
                return False
            if len(idea["first_steps"]) == 0:
                return False
            if len(idea["tech_recommendations"]) == 0:
                return False

        return True
    except Exception:
        return False


def get_fallback_ideas(profile: UserProfile, num_ideas: int, db: Session) -> GenerationResponse:
    """Return safe, pre-validated ideas when AI generation fails."""
    logger.info("Generating fallback ideas from database")

    # Get matching ideas from database
    source_ideas = get_matching_ideas(profile, db, limit=num_ideas)

    fallback_ideas = []
    for idea in source_ideas[:num_ideas]:
        # Convert database idea to generated idea format
        fallback = GeneratedIdea(
            title=idea.title,
            description=idea.summary or idea.description or "A proven idea from successful creators",
            why_good_fit=f"Matches your {profile.experience_level} level and interests",
            first_steps=[
                "Research similar projects in this space",
                "Sketch out basic features and user flow",
                "Build a simple MVP to test the concept"
            ],
            tech_recommendations=idea.tech_stack[:3] if idea.tech_stack else profile.technical_skills[:3],
            source_idea_ids=[idea.id],
        )
        fallback_ideas.append(fallback)

    # If still not enough ideas, create generic safe ones
    while len(fallback_ideas) < num_ideas:
        fallback_ideas.append(create_safe_generic_idea(profile, len(fallback_ideas)))

    return GenerationResponse(
        ideas=fallback_ideas[:num_ideas],
        profile_summary=f"Based on your {profile.experience_level} level profile",
    )


def create_safe_generic_idea(profile: UserProfile, index: int) -> GeneratedIdea:
    """Create a safe generic idea based on user skills."""
    skills = profile.technical_skills if profile.technical_skills else ["HTML", "CSS", "JavaScript"]

    generic_ideas = [
        {
            "title": "Portfolio Website with Blog",
            "description": "Build a personal portfolio website to showcase your skills and projects. Add a blog to share your learning journey and attract opportunities.",
            "tech": skills[:2] if len(skills) >= 2 else skills,
        },
        {
            "title": "Simple Automation Tool",
            "description": "Create a tool that automates a repetitive task you do regularly. Start small and expand based on feedback.",
            "tech": skills[:2] if len(skills) >= 2 else skills,
        },
        {
            "title": "Learning Resource Aggregator",
            "description": "Build a curated collection of resources for learning a skill you're passionate about. Help others on the same journey.",
            "tech": skills[:2] if len(skills) >= 2 else skills,
        },
    ]

    idea_template = generic_ideas[index % len(generic_ideas)]

    return GeneratedIdea(
        title=idea_template["title"],
        description=idea_template["description"],
        why_good_fit=f"Uses your existing skills: {', '.join(idea_template['tech'])}",
        first_steps=[
            "Define the core problem you're solving",
            "Sketch out the basic user experience",
            "Build a minimal working version"
        ],
        tech_recommendations=idea_template["tech"],
        source_idea_ids=[],
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
If no inspiration ideas provided, create ideas based purely on user profile.

CRITICAL: Only suggest technologies from their Technical Skills list above."""


SYSTEM_PROMPT = """You are a startup idea generator. Create NEW, ORIGINAL project ideas for users based on their profile and patterns from successful ideas.

STRICT RULES - YOU MUST FOLLOW THESE:
1. ONLY suggest technologies and tools the user ALREADY KNOWS from their technical_skills
2. NEVER suggest technologies the user has not listed in their skills
3. NEVER exceed the user's stated budget - if budget is "free", suggest ONLY free tools
4. MATCH difficulty to experience level - beginners get beginner-friendly stacks only
5. If user is beginner, suggest simple, well-documented technologies (Python, HTML/CSS, no complex frameworks)
6. Tech recommendations MUST overlap with user's technical_skills by at least 50%
7. Do NOT suggest paid services, premium tools, or infrastructure costs if budget is "free" or "<$100"
8. For beginners, avoid: Kubernetes, Docker, microservices, Redis, GraphQL, complex frameworks
9. NEVER suggest: AWS, Azure, GCP, OpenAI API, or paid services if budget is "free"

Your ideas should:
1. Match the user's EXISTING skill set (do not stretch unless they are intermediate+)
2. Stay WITHIN their budget constraints
3. Match their experience level exactly
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
