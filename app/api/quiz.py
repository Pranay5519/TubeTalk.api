from fastapi import APIRouter, HTTPException , Depends
from app.models.quiz_model import QuizList
from app.services.quiz_service import QuizGenerator
from app.utils.utility_functions import load_transcript
from app.core.auth import get_gemini_api_key
router = APIRouter(prefix="/quiz", tags=["quiz"])

@router.post("/generate_quiz", response_model=QuizList)
async def generate_quiz(url: str,api_key : str = Depends(get_gemini_api_key)):
    """Generate a quiz from YouTube video URL"""
    quiz_generator = QuizGenerator(api_key=api_key)
    captions = load_transcript(url)
    if not captions:
        raise HTTPException(status_code=404, detail="No transcript found for this video.")
    
    quiz = await quiz_generator.generate_quiz(captions)
    return {"quizzes": quiz.quizzes}  
