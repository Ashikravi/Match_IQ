from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.extractor import (
    extract_text_from_pdf,
    extract_skills,
    read_upload_file
)
from app.services.matcher import calculate_match_score
from app.schemas import MatchResponse, ExtractResponse

router = APIRouter()


@router.post("/match", response_model=MatchResponse)
async def match_resume(
    resume: UploadFile = File(...),
    jd_text: str = Form(...)
):
    """
    Upload a resume PDF and paste a job description.
    Returns a semantic match score with skill gap analysis.
    """
    # Validate file type
    if not resume.filename.endswith(".pdf"): # type: ignore
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

    return MatchResponse(
        filename=resume.filename,
        scores=result["scores"],
        skills=result["skills"]
    )


@router.post("/extract", response_model=ExtractResponse)
async def extract_resume(
    file: UploadFile = File(...)
):
    """
    Upload a resume PDF.
    Returns extracted text and detected skills.
    """
    if not file.filename.endswith(".pdf"):
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
        filename=file.filename,
        character_count=len(text),
        skills_found=skills,
        text=text
    )