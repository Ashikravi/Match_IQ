from fastapi import FastAPI
from app.routers import match
from app.db.database import engine, Base

#creates all tables defined in models on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MatchIQ",
    description="Semantic resume-JD matching engine",
    version="1.0.0"
)

app.include_router(match.router, prefix="/api/v1", tags=["Match"])

@app.get("/health")
def health_check():
    return {"status": "ok"}