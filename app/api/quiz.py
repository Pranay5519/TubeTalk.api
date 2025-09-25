from fastapi import APIRouter, HTTPException
from app.models.quiz_model import QuizList
from app.services.quiz_service import QuizGenerator
from app.utils.utility_functions import load_transcript

router = APIRouter(prefix="/quiz", tags=["quiz"])

@router.post("/generate_quiz", response_model=QuizList)
async def generate_quiz(url: str):
    """Generate a quiz from YouTube video URL"""
    quiz_generator = QuizGenerator()
    captions = load_transcript(url)
    
    if not captions:
        raise HTTPException(status_code=404, detail="No transcript found for this video.")
    
    quiz = await quiz_generator.generate_quiz(captions)
    return {"quizzes": quiz.quizzes}  
