from fastapi import APIRouter
from app.models.topics_model import Subtopic, MainTopic, TopicsOutput
from app.services.topics_service import TopicGenerator
from app.utils.utility_functions import load_transcript
from fastapi import APIRouter, HTTPException
router = APIRouter(prefix="/topics", tags=["topics"])


@router.post("/get_topics", response_model=TopicsOutput)
def generate_topics(url: str):
    """Generate structured topics from YouTube video URL"""
    analyzer = TopicGenerator()
    captions = load_transcript(url)
    if captions:
        segments = analyzer.parse_transcript(captions)
        formatted = [f"[{seg.start_time}s] {seg.text}" for seg in segments]
        response = analyzer.extract_topics(" ".join(formatted))
        return {"main_topics": response.main_topics}
    else:
        raise HTTPException(status_code=404, detail="No transcript found for this video.")
    
    