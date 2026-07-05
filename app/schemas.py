from pydantic import BaseModel


class ScoreBreakdown(BaseModel):
    full_document: float
    skills_section: float
    experience_section: float


class ScoreDetail(BaseModel):
    overall: float
    percentage: float
    label: str
    breakdown: ScoreBreakdown


class SkillDetail(BaseModel):
    matched: list[str]
    gaps: list[str]
    extras: list[str]


class MatchResponse(BaseModel):
    filename: str
    scores: ScoreDetail
    skills: SkillDetail


class ExtractResponse(BaseModel):
    filename: str
    character_count: int
    skills_found: list[str]
    text: str