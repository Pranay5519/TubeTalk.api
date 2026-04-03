from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.pydantic_models.topics_model import TopicsOutput
from app.services.topics_service import TopicGenerator
from app.services.summary_service import SummaryGenerator
from app.utils.utility_functions import load_transcript
from app.core.auth import get_gemini_api_key
from app.database.database import Base, engine, SessionLocal
from app.database.crud import save_topics_to_db, load_topics_from_db ,  save_url_to_db, save_summary_to_db
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger("uvicorn")  # Use the same logger as main.py

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(prefix="/topics", tags=["topics"])

@router.post("/get_topics", response_model=TopicsOutput)
async def generate_or_load_topics(
    url: str,
    thread_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_gemini_api_key)
):
    """Generate structured topics from YouTube video URL"""
    
    # Try to load existing topics
    existing_topics = load_topics_from_db(db, thread_id)
    if existing_topics:
        logger.info(f"Returning existing topics for thread_id: {thread_id}") 
        return existing_topics

    logger.info(f"🧠 No existing topics for {thread_id}, starting One-Pass Generation for both Topics & Summary.")
    
    summary_generator = SummaryGenerator(api_key=api_key)
    captions = load_transcript(url)
    
    if not captions:
        raise HTTPException(status_code=404, detail="❌ No transcript found for this video.")
    
    # ONE-PASS OPTIMIZATION: Generate both Topics and Summary in a single call
    combined_result = await summary_generator.generate_topics_and_summary(captions)
    topics = combined_result.topics
    summary = combined_result.summary

    if topics:
        try:
            # Save both to database (reduces future LLM calls)
            await run_in_threadpool(save_topics_to_db, db, thread_id, topics)
            await run_in_threadpool(save_summary_to_db, db, thread_id, summary)
            await run_in_threadpool(save_url_to_db, db, thread_id, url)
            
            logger.info(f"✅ Topics and Summary saved for thread_id: {thread_id}")
            return topics  
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"⚠️ Failed to save data: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to save generated data: {str(e)}")
    
    raise HTTPException(status_code=500, detail="Failed to generate topics.")
