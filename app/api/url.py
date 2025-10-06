from fastapi import APIRouter, Depends, HTTPException
from app.core.auth import get_gemini_api_key
from app.database.crud import load_url_from_db
from sqlalchemy.orm import Session
from app.database.database import Base, engine, SessionLocal



# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(prefix="/get_url", tags=["url"])
@router.post("/get_url")
async def get_url(
    thread_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_gemini_api_key)
):
    url_entry = load_url_from_db(db, thread_id)  # ✅ Pass db as first argument

    if not url_entry:
        raise HTTPException(status_code=404, detail="URL not found for this thread_id")

    return {
        "thread_id": thread_id,
        "url": url_entry.url
    }
