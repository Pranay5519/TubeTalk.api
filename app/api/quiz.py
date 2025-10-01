from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.pydantic_models.quiz_model import QuizList
from app.services.quiz_service import QuizGenerator
from app.utils.utility_functions import load_transcript
from app.core.auth import get_gemini_api_key
from app.database.database import Base, engine, SessionLocal
from app.database.crud import save_quiz_to_db, load_quiz_from_db
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.exc import SQLAlchemyError
import logging
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
router = APIRouter(prefix="/quiz", tags=["quiz"])
@router.post("/generate_quiz", response_model=QuizList)
async def generate_or_load_quiz(
    url: str,
    thread_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_gemini_api_key)
):
    """
    Return existing quiz for thread_id if available,
    else generate a new quiz from YouTube URL.
    """
    # Try to load existing quiz
    existing_quiz = load_quiz_from_db(db, thread_id)
    if existing_quiz:
        logging.info(f"Returning existing quiz for thread_id: {thread_id}") 
        return existing_quiz
    logging.info(f"No existing quiz for thread_id: {thread_id}, generating new one.")
    # No existing quiz, generate new one
    quiz_generator = QuizGenerator(api_key=api_key)
    captions = load_transcript(url)
    if not captions:
        raise HTTPException(status_code=404, detail="No transcript found for this video.")

    quiz = await quiz_generator.generate_quiz(captions)

    if quiz:
        try:
            # Save new quiz to DB
            await run_in_threadpool(save_quiz_to_db, db, thread_id, quiz)
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to save quiz: {str(e)}")

    return {"quizzes" : quiz.quizzes}  # QuizList object
