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
from app.database.crud import save_summary_to_db, load_summary_from_db , load_topics_from_db , save_topics_to_db
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
    """Generate structured topics and summary from YouTube video URL"""
    
    existing_summary = load_summary_from_db(db, thread_id)
    existing_topics = load_topics_from_db(db, thread_id)
    if existing_summary :
        logger.info(f"Returning existing summary for thread_id: {thread_id}") 
        return {
        "main_summary": existing_summary.main_summary
    }
    
    logger.info(f"No existing summary for thread_id: {thread_id}, generating new one.")
    # No existing summary, generate new one
    
    topics_generator = TopicGenerator(api_key=api_key)
    summary_generator = SummaryGenerator(api_key=api_key)

    captions = load_transcript(url)
    if not captions:
        raise HTTPException(status_code=404, detail="No transcript found for this video.")
    
    if existing_topics:
        logger.info(f"Using existing topics for thread_id: {thread_id}") 
        topics = existing_topics.main_topics
    # Parse transcript into segments
    else:
        logger.info(f"No existing topics for thread_id: {thread_id}, generating new one.") 
        segments = topics_generator.parse_transcript(captions)
        formatted = [f"[{seg.start_time}s] {seg.text}" for seg in segments]
        # Extract topics
        response = await topics_generator.extract_topics(" ".join(formatted))
        topics = response.main_topics
        if response:
            try:
                topics_outupt = TopicsOutput(main_topics=topics)
                await run_in_threadpool(save_topics_to_db , db , thread_id , topics_outupt)
                logger.info(f"Topics saved  for thread_id : {thread_id}")
            except SQLAlchemyError as e:
                db.rollback()
                raise HTTPException(status_code=500, detail=f"Failed to save topics: {str(e)}")
            
    # Generate summary (await because it's async)
    summary = await summary_generator.generate_summary(captions, str(topics))
    if summary:
        try:
            # Save new quiz to DB
            logger.info(f"Summary Saved for thread_id: {thread_id}")
            await run_in_threadpool(save_summary_to_db, db, thread_id, summary)
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to save quiz: {str(e)}")

    return {
        "main_summary": summary.main_summary,
    }
