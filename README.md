# MatchIQ

A semantic resume-to-job-description matching engine built with FastAPI.
Upload a resume PDF and paste a job description — MatchIQ returns a
relevance score, matched skills, and gaps using sentence embeddings
and cosine similarity.

---

## Why semantic matching?

Keyword matching counts shared words between a resume and JD.
It fails when a resume says "built REST endpoints" and the JD says
"API development experience" — different words, same meaning.

MatchIQ uses `sentence-transformers` to convert both texts into
384-dimensional vectors that capture meaning, not just words.
Cosine similarity then measures the angle between those vectors.
Small angle = similar meaning = high score, regardless of exact wording.

---

## Architecture

```
POST /api/v1/match
        │
        ├── extractor.py   → PDF bytes → clean text (pdfplumber)
        ├── embedder.py    → text → 384-dim vector (all-MiniLM-L6-v2)
        ├── matcher.py     → cosine similarity → weighted score + gap analysis
        └── MySQL          → stores match result with timestamp
```

**Matching is section-level, not just full-document:**

| Layer | Weight | Reason |
|---|---|---|
| Full document | 30% | Overall context signal |
| Skills section | 50% | Primary signal for fresher roles |
| Experience section | 20% | Supporting signal |

---

## Tech Stack

| Technology | Purpose |
|---|---|
| FastAPI | API framework — async, auto-docs via Swagger UI |
| sentence-transformers | Text → embeddings (all-MiniLM-L6-v2) |
| scikit-learn | Cosine similarity calculation |
| pdfplumber | PDF text extraction |
| SQLAlchemy | ORM for MySQL |
| MySQL | Persistent match result storage |
| Docker + Compose | Containerised deployment |

---

## Project Structure

```
matchiq/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── schemas.py           # Pydantic request/response models
│   ├── routers/
│   │   └── match.py         # API route definitions
│   ├── services/
│   │   ├── extractor.py     # PDF extraction + skill detection
│   │   ├── embedder.py      # Sentence embedding
│   │   └── matcher.py       # Scoring + gap analysis
│   └── db/
│       ├── database.py      # SQLAlchemy engine + session
│       └── models.py        # MatchResult table definition
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Running Locally

**With Docker (recommended):**

```bash
git clone https://github.com/yourusername/matchiq.git
cd matchiq
docker-compose up --build
```

Open `http://localhost:8000/docs`

**Without Docker:**

```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` in the root:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=matchiq
```

Create the database:

```sql
CREATE DATABASE matchiq;
```

Run the server:

```bash
uvicorn app.main:app --reload
```

---

## API Reference

### `POST /api/v1/match`

Upload a resume PDF and paste a job description. Returns a semantic
match score with section-level breakdown and skill gap analysis.

**Request:** `multipart/form-data`

| Field | Type | Description |
|---|---|---|
| resume | PDF file | Candidate resume |
| jd_text | string | Job description text |

**Response:**

```json
{
  "filename": "resume.pdf",
  "scores": {
    "overall": 0.7234,
    "percentage": 72.34,
    "label": "Moderate Match",
    "breakdown": {
      "full_document": 0.6821,
      "skills_section": 0.7654,
      "experience_section": 0.6912
    }
  },
  "skills": {
    "matched": ["docker", "fastapi", "python"],
    "gaps": ["kubernetes", "postgresql"],
    "extras": ["django", "git"]
  }
}
```

---

### `POST /api/v1/extract`

Upload a resume PDF. Returns extracted text and detected skills.
Useful for verifying extraction quality before running a full match.

**Request:** `multipart/form-data`

| Field | Type | Description |
|---|---|---|
| file | PDF file | Candidate resume |

**Response:**

```json
{
  "filename": "resume.pdf",
  "character_count": 1842,
  "skills_found": ["python", "fastapi", "docker", "mysql"],
  "text": "ASHIK RAVI ..."
}
```

---

### `GET /api/v1/history`

Returns the last 20 match results stored in the database.

**Response:**

```json
[
  {
    "id": 1,
    "filename": "resume.pdf",
    "score": 0.7234,
    "percentage": 72.34,
    "label": "Moderate Match",
    "matched_skills": ["python", "fastapi"],
    "gaps": ["kubernetes"],
    "created_at": "2025-01-15T10:30:00"
  }
]
```

---

## Known Limitations

- LaTeX-generated PDFs may produce concatenated words due to custom
  font encoding. Standard PDFs exported from Word or Google Docs
  extract cleanly.

- Skill detection uses a keyword list — it catches common technologies
  but won't detect niche or domain-specific tools not in the list.

- Full-document embedding averages all section meanings. Section-level
  matching partially addresses this but very long resumes may still
  dilute the skills signal.

---

## What I would build next

- [ ] React frontend with score visualisation
- [ ] pgvector for storing and querying embeddings directly with PostgreSQL
- [ ] Per-role weight profiles (fresher vs senior vs specialist)
- [ ] Support for DOCX resume format