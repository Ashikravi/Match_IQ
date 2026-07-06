from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.sql import func
from app.db.database import Base


class MatchResult(Base):
    __tablename__ = "match_results"

    id = Column(Integer, primary_key=True, index=True)
    
    # Input
    filename = Column(String(255), nullable=False)
    
    # Scores
    overall_score = Column(Float, nullable=False)
    percentage = Column(Float, nullable=False)
    label = Column(String(50), nullable=False)
    
    # Section scores
    full_document_score = Column(Float)
    skills_section_score = Column(Float)
    experience_section_score = Column(Float)
    matched_skills = Column(Text, nullable=True)
    gap_skills = Column(Text, nullable=True)
    extra_skills = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())