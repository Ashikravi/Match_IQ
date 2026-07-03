from fastapi import FastAPI
from app.routers import match

app = FastAPI(
    title="MatchIQ",
    description="Semantic resume-JD matching engine",
    version="1.0.0"
)

app.include_router(match.router, prefix="/api/v1", tags=["Match"])

@app.get("/health")
def health_check():
    return {"status": "ok"}