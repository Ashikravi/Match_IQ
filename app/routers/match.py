from fastapi import APIRouter

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.extractor import extract_text_from_pdf, read_upload_file

router = APIRouter()


@router.post("/extract")
async def extract_resume(file: UploadFile = File(...)):
    # Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files accepted")

    # Read the uploaded file into bytes
    file_bytes = await read_upload_file(file)

    # Extract and clean text
    extracted_text = extract_text_from_pdf(file_bytes)

    if not extracted_text:
        raise HTTPException(status_code=422, detail="Could not extract text. PDF may be image-based.")

    return {
        "filename": file.filename,
        "character_count": len(extracted_text),
        "text": extracted_text
    }