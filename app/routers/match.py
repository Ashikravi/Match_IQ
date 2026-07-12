from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from app.services.extractor import (
    extract_text_from_pdf,
    extract_skills,
    read_upload_file
)
from app.services.matcher import calculate_match_score
from app.schemas import MatchResponse, ExtractResponse
from app.db.database import get_db
from app.db import models


router = APIRouter()

@router.post("/match", response_model=MatchResponse)
async def match_resume(
    resume: UploadFile = File(...),
    jd_text: str = Form(...),
    db:Session = Depends(get_db)
    
):
    """
    Upload a resume PDF and paste a job description.
    Returns a semantic match score with skill gap analysis.
    """
    # Validate file type
    filename = resume.filename or "unknown.pdf"
    if not filename.endswith(".pdf"): 
        raise HTTPException(
            status_code=400,
            detail="Only PDF files accepted"
        )

    # Validate JD not empty
    if not jd_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty"
        )

    # Read and extract resume text
    file_bytes = await read_upload_file(resume)
    resume_text = extract_text_from_pdf(file_bytes)

    if not resume_text:
        raise HTTPException(
            status_code=422,
            detail="Could not extract text from PDF"
        )

    # Run matching
    result = calculate_match_score(resume_text, jd_text)
    # Save to database
    db_record = models.MatchResult(
        filename= filename,
        overall_score=result["scores"]["overall"],
        percentage=result["scores"]["percentage"],
        label=result["scores"]["label"],
        full_document_score=result["scores"]["breakdown"]["full_document"],
        skills_section_score=result["scores"]["breakdown"]["skills_section"],
        experience_section_score=result["scores"]["breakdown"]["experience_section"],
        matched_skills=",".join(result["skills"]["matched"]),
        gap_skills=",".join(result["skills"]["gaps"]),
        extra_skills=",".join(result["skills"]["extras"])
    )
    db.add(db_record)
    db.commit()

    return MatchResponse(
        filename = filename,
        scores = result["scores"],
        skills = result["skills"]
    )

@router.get("/history")
def get_match_history(db: Session = Depends(get_db)):
    """
    Returns the last 20 match results.
    """
    records = db.query(models.MatchResult)\
                .order_by(models.MatchResult.created_at.desc())\
                .limit(20)\
                .all()

    return [
        {
            "id": r.id,
            "filename": r.filename,
            "score": r.overall_score,
            "percentage": r.percentage,
            "label": r.label,
            "matched_skills": r.matched_skills.split(",") if r.matched_skills is not None else [],
            "gaps": r.gap_skills.split(",") if r.gap_skills is not None else [],
            "extra_skills": r.extra_skills.split(",") if r.extra_skills is not None else [],
            "created_at": r.created_at
        }
        for r in records
    ]
    
@router.post("/extract", response_model=ExtractResponse)
async def extract_resume(
    file: UploadFile = File(...)
):
    """
    Upload a resume PDF.
    Returns extracted text and detected skills.
    """
    filename = file.filename or "unknown.pdf"
    if not filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files accepted"
        )

    file_bytes = await read_upload_file(file)
    text = extract_text_from_pdf(file_bytes)

    if not text:
        raise HTTPException(
            status_code=422,
            detail="Could not extract text from PDF"
        )

    skills = extract_skills(text)

    return ExtractResponse(
        filename= filename,
        character_count=len(text),
        skills_found=skills,
        text=text
    )