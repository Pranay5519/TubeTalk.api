from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.crud import get_all_thread_ids

router = APIRouter(prefix="/thread_ids", tags=["thread_ids"])

@router.get("/all_conversations")
def all_conversations(db: Session = Depends(get_db)):
    thread_ids = get_all_thread_ids(db)
    return {"conversations": thread_ids}
