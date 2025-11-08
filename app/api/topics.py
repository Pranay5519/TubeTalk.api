from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.pydantic_models.topics_model import TopicsOutput
from app.services.topics_service import TopicGenerator
from app.utils.utility_functions import load_transcript
from app.core.auth import get_gemini_api_key
from app.database.database import Base, engine, SessionLocal
from app.database.crud import save_topics_to_db, load_topics_from_db ,  save_url_to_db
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

    logger.info(f"No existing topics for thread_id: {thread_id}, generating new one.")
    
    analyzer = TopicGenerator(api_key=api_key)
    captions = load_transcript(url)
    
    if not captions:
        raise HTTPException(status_code=404, detail="No transcript found for this video.")
    
    # No need to parse transcript into segments it does not make much difference in output
    #segments = analyzer.parse_transcript(captions)
    #formatted = [f"[{seg.start_time}s] {seg.text}" for seg in segments]

    response = await analyzer.extract_topics(captions)  # async call

    if response:
        try:
            topics_output = TopicsOutput(main_topics=response.main_topics)  # Convert to Pydantic model
            await run_in_threadpool(save_topics_to_db, db, thread_id, topics_output)
            await run_in_threadpool(save_url_to_db, db, thread_id, url)
            logger.info(f"Topics saved for thread_id: {thread_id}")
            return topics_output  # Always return Pydantic model
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Failed to save topics for thread_id {thread_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to save topics: {str(e)}")
    
    # If response is empty
    raise HTTPException(status_code=404, detail="No topics could be generated.")
