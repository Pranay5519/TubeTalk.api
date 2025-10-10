from fastapi import APIRouter, Depends, HTTPException
from app.database.crud import load_url_from_db
from sqlalchemy.orm import Session
from app.database.database import get_db

router = APIRouter(prefix="/url", tags=["url"])

@router.get("/{thread_id}")
async def get_url(
    thread_id: str,
    db: Session = Depends(get_db),
    ):
    url_entry = load_url_from_db(db, thread_id)

    if not url_entry:
        raise HTTPException(status_code=404, detail="URL not found for this thread_id")

    return {
        "thread_id": thread_id,
        "url": url_entry.url
    }
