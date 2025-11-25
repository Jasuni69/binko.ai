from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.profile import UserProfile
from app.schemas.generation import GenerationRequest, GenerationResponse
from app.services.generation import generate_ideas

router = APIRouter()


@router.post("", response_model=GenerationResponse)
async def generate(request: GenerationRequest, db: Session = Depends(get_db)):
    result = await generate_ideas(request.profile, request.num_ideas, db)
    return result
