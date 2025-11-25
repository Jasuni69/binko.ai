from sqlalchemy import Column, String, Text, Float, ARRAY
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database import Base


class Idea(Base):
    __tablename__ = "ideas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Core
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    description = Column(Text)

    # Classification
    idea_type = Column(String(50))  # saas, service, product, content, marketplace
    business_model = Column(String(50))  # subscription, one_time, freemium, ads
    monetization = Column(Text)

    # Requirements
    skills = Column(ARRAY(String))  # ['python', 'marketing', 'design']
    tech_stack = Column(ARRAY(String))
    difficulty = Column(String(20))  # beginner, intermediate, advanced
    time_to_mvp = Column(String(50))  # 1 week, 1 month, 3 months
    startup_cost = Column(String(50))  # free, <$100, <$1000

    # Market
    target_audience = Column(Text)
    niche = Column(String(100))
    competition = Column(String(20))  # low, medium, high

    # Details
    key_features = Column(ARRAY(String))
    success_factors = Column(ARRAY(String))
    challenges = Column(ARRAY(String))

    # Source
    source_video_id = Column(String(50))
    source_channel = Column(String(255))
    confidence = Column(Float)
