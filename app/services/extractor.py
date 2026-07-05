import pdfplumber
import re 
from fastapi import UploadFile
import io
def extract_text_from_pdf(file_bytes: bytes) -> str:
    print("extractor runnning")
    text = ""

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            # extract_words() finds individual word bounding boxes
            # joining them with space guarantees word boundaries
            words = page.extract_words()
            if words:
                page_text = ' '.join([word['text'] for word in words])
                text += page_text + "\n"

    return clean_text(text)

def clean_text(text: str) -> str:
    """
    Raw PDF text is messy — extra spaces, weird line breaks, 
    unicode artifacts. This fixes that.
    """
    #latex code bullets
    text = re.sub(r'\(cid:\d+\)', ' ', text)
    # Replace multiple whitespace/newlines with single space
    text = re.sub(r'\s+', ' ', text)
     # Remove non-ASCII characters (unicode artifacts from PDFs)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


async def read_upload_file(file: UploadFile) -> bytes:
    """
    FastAPI's UploadFile is an async file object.
    This reads it into bytes so pdfplumber can use it.
    """
    return await file.read()

# Common tech skills to look for
# This list is intentionally broad — covers most JDs you'll see
SKILL_KEYWORDS = [
    # Languages
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust",
    "sql", "html", "css",
    # Frameworks
    "fastapi", "django", "flask", "react", "nodejs", "express", "spring",
    # Databases
    "mysql", "postgresql", "mongodb", "redis", "sqlite",
    # DevOps
    "docker", "kubernetes", "git", "aws", "gcp", "azure", "linux",
    "ci/cd", "jenkins", "github actions",
    # AI/ML
    "machine learning", "deep learning", "nlp", "scikit-learn",
    "tensorflow", "pytorch", "hugging face", "transformers",
    "langchain", "vector database", "rag",
    # Concepts
    "rest api", "restful", "microservices", "agile", "system design"
]


def extract_skills(text: str) -> list[str]:
    """
    Scans text for known skill keywords.
    Returns a list of matched skills in lowercase.
    """
    text_lower = text.lower()
    found = []

    for skill in SKILL_KEYWORDS:
        if skill in text_lower:
            found.append(skill)

    return found


def extract_section(text: str, section_name: str) -> str:
    """
    Tries to pull out a specific section from resume text.
    Looks for the section header and takes text until the next header.
    
    Common headers: SKILLS, EXPERIENCE, EDUCATION, PROJECTS
    """
    text_upper = text.upper()
    section_upper = section_name.upper()

    start = text_upper.find(section_upper)
    if start == -1:
        return ""  # section not found, return empty string

    # Find where the next section starts
    # Look for common section headers after our section
    next_headers = ["EXPERIENCE", "EDUCATION", "PROJECTS",
                    "SKILLS", "CERTIFICATIONS", "OBJECTIVE", "SUMMARY"]

    end = len(text)
    for header in next_headers:
        if header == section_upper:
            continue
        pos = text_upper.find(header, start + len(section_name))
        if pos != -1 and pos < end:
            end = pos

    return text[start:end].strip()