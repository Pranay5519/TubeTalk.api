from fastapi import APIRouter , Depends
from app.pydantic_models.topics_model import  MainTopic , TopicsOutput
from app.pydantic_models.summay_model import SummaryOutput
from typing import List
from pydantic import BaseModel
from app.services.topics_service import TopicGenerator
from app.utils.utility_functions import load_transcript
from app.services.summary_service import SummaryGenerator
from fastapi import APIRouter, HTTPException
from app.core.auth import get_gemini_api_key
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.database.database import Base, engine, SessionLocal
from app.database.crud import save_summary_to_db, load_summary_from_db , load_topics_from_db , save_topics_to_db , save_url_to_db
import logging
logger = logging.getLogger("uvicorn")

Base.metadata.create_all(bind=engine)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(prefix="/summary", tags=["summary"])


@router.post("/get_summary", response_model=SummaryOutput)
async def generate_or_load_summary(url: str,
                                thread_id: str,
                                db: Session = Depends(get_db),
                                api_key: str = Depends(get_gemini_api_key)):
    """Generate structured topics and summary from YouTube video URL using One-Pass optimization"""
    
    # 1. Check for existing data
    existing_summary = load_summary_from_db(db, thread_id)
    existing_topics = load_topics_from_db(db, thread_id)
    
    if existing_summary:
        logger.info(f"🚀 Returning existing summary for thread_id: {thread_id}") 
        return {"main_summary": existing_summary.main_summary}
    
    # 2. If missing, generate everything in "One Pass"
    logger.info(f"🧠 No existing summary for {thread_id}, starting One-Pass Generation.")
    summary_generator = SummaryGenerator(api_key=api_key)

    captions = load_transcript(url)
    if not captions:
        raise HTTPException(status_code=404, detail="❌ No transcript found for this video.")
    
    # Optimization: One-Pass (Topic + Summary in one call)
    # This is more token-efficient than passing both transcript and topics separately
    combined_result = await summary_generator.generate_topics_and_summary(captions)
    topics_output = combined_result.topics
    summary = combined_result.summary

    # Cache both immediately
    try:
        await run_in_threadpool(save_topics_to_db, db, thread_id, topics_output)
        await run_in_threadpool(save_summary_to_db, db, thread_id, summary)
        await run_in_threadpool(save_url_to_db, db, thread_id, url)
        logger.info(f"✅ Topics and Summary saved for {thread_id}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"⚠️ Failed to save data: {e}")
        # We don't necessarily raise here if the generation succeeded, 
        # but let's be consistent with previous error handling
        raise HTTPException(status_code=500, detail=f"❌ Failed to save results: {str(e)}")

    return {"main_summary": summary.main_summary}
