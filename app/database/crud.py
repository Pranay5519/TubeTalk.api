from sqlalchemy.orm import Session
from app.database.models import Quiz
from datetime import datetime
from app.models.quiz_model import Quiz as PydanticQuiz, QuizList
import json

def save_quiz_to_db(db: Session, thread_id: str, quiz_list: QuizList):
    """
    Save a list of quizzes into the database.
    Converts list of Pydantic quiz objects to JSON string before saving.
    """
    # Convert Pydantic objects to dict, then JSON string
    quiz_json = json.dumps([quiz.model_dump() for quiz in quiz_list.quizzes])

    new_quiz = Quiz(
        thread_id=thread_id,
        quiz=quiz_json,  # save as JSON string
        created_at=datetime.now()
    )
    db.add(new_quiz)
    db.commit()
    db.refresh(new_quiz)
    return new_quiz

def load_quiz_from_db(db: Session, thread_id: str) -> QuizList | None:
    """
    Load quizzes from the database for a given thread_id.
    Returns a QuizList object or None if not found.
    """
    # Fetch the latest quiz row for the given thread_id
    quiz_row = db.query(Quiz).filter(Quiz.thread_id == thread_id).order_by(Quiz.created_at.desc()).first()

    if not quiz_row:
        return None  # no quiz found

    # Convert JSON string back to list of Quiz objects
    quiz_dicts = json.loads(quiz_row.quiz)
    quizzes = [PydanticQuiz(**qd) for qd in quiz_dicts]  # Pydantic objects
    return QuizList(quizzes=quizzes)

