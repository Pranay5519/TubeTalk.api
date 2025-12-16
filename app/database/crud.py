from sqlalchemy.orm import Session
from app.database.models import Quiz , Summary , Topics
from datetime import datetime
from app.pydantic_models.quiz_model import Quiz as PydanticQuiz, QuizList
from app.pydantic_models.topics_model import TopicsOutput
from app.pydantic_models.summay_model import SummaryOutput
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

    return None
def save_topics_to_db(db: Session, thread_id: str, topics: TopicsOutput):
    """
    Save transcript topics into the database.
    Converts TopicsOutput Pydantic object to JSON before saving.
    """
    topics_json = topics.model_dump_json()  # convert Pydantic -> JSON string

    new_topics = Topics(
        thread_id=thread_id,
        output_json=topics_json,
        created_at=datetime.now()
    )
    db.add(new_topics)
    db.commit()
    db.refresh(new_topics)
    return new_topics
def load_topics_from_db(db: Session, thread_id: str) -> TopicsOutput | None:
    """
    Load transcript topics from the database using thread_id.
    Returns a TopicsOutput object if found, else None.
    """
    result = (
        db.query(Topics)
        .filter(Topics.thread_id == thread_id)
        .order_by(Topics.created_at.desc())
        .first()
    )

    if result:
        try:
            data = json.loads(result.output_json)  # string -> dict
            return TopicsOutput.model_validate(data)  # dict -> Pydantic object
        except Exception as e:
            print("Error loading TopicsOutput from DB:", e)
            return None
    return None

def save_summary_to_db(db: Session, thread_id: str, summary_text: SummaryOutput):
    summary_json = summary_text.model_dump_json()# Convert Pydantic → str JSON
    new_summary = Summary(
        thread_id=thread_id,
        summary=summary_json,  
        created_at=datetime.now()
    )
    db.add(new_summary)
    db.commit()
    db.refresh(new_summary)
    return new_summary

def load_summary_from_db(db: Session, thread_id: str) -> SummaryOutput | None:
    """
    Check if a summary for the given thread_id exists in the database.
    Returns the structured SummaryOutput if found, else None.
    """
    summary_obj = db.query(Summary).filter(Summary.thread_id == thread_id).first()
    if summary_obj and summary_obj.summary:
        # Convert JSON string back to Pydantic object
        summary_dict = json.loads(summary_obj.summary)
        return SummaryOutput.model_validate(summary_dict)  # or model_validate_json(summary_obj.summary)
    return None


import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.database.models import YouTubeData  # your video_url model

def save_url_to_db(db: Session, thread_id: str, url: str):
    """
    Save a YouTube URL and thread_id into the database.
    If the same thread_id already exists, skip saving.
    """
    existing_entry = db.query(YouTubeData).filter_by(thread_id=thread_id).first()

    if not existing_entry:
        new_entry = YouTubeData(
            thread_id=thread_id,
            url=url,
            created_at=datetime.utcnow()
        )
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)
        return new_entry
    return existing_entry  # Return existing if already present

def load_url_from_db(db: Session, thread_id: str):
    """
    Load a stored YouTube URL from the database by thread_id.

    Args:
        db (Session): Active SQLAlchemy session.
        thread_id (str): Unique identifier for the video/thread.

    Returns:
        YouTubeData | None: The database entry if found, else None.
    """
    return db.query(YouTubeData).filter_by(thread_id=thread_id).first()



from sqlalchemy.orm import Session
from app.database.models import YouTubeData

def get_all_thread_ids(db: Session):
    """
    Fetch all unique thread_ids stored in the video_url table using SQLAlchemy.
    """
    thread_objs = db.query(YouTubeData.thread_id).distinct().all()
    thread_ids = [t[0] for t in thread_objs]
    return thread_ids
