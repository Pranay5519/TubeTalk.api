from fastapi import APIRouter
from app.models.topics_model import  MainTopic
from typing import List
from pydantic import BaseModel
from app.services.topics_service import TopicGenerator
from app.utils.utility_functions import load_transcript
from app.services.summary_service import SummaryGenerator
from fastapi import APIRouter, HTTPException
router = APIRouter(prefix="/summary", tags=["summary"])

class SummaryResponse(BaseModel):
    topics: List[MainTopic]
    summary: str

@router.post("/get_summary", response_model=SummaryResponse)
async def generate_summary(url: str):
    """Generate structured topics and summary from YouTube video URL"""
    topics_generator = TopicGenerator()
    summary_generator = SummaryGenerator()

    captions = load_transcript(url)
    if not captions:
        raise HTTPException(status_code=404, detail="No transcript found for this video.")
    

    # Parse transcript into segments
    segments = topics_generator.parse_transcript(captions)
    formatted = [f"[{seg.start_time}s] {seg.text}" for seg in segments]

    # Extract topics
    response = topics_generator.extract_topics(" ".join(formatted))

    # Generate summary (await because it's async)
    summary = await summary_generator.generate_summary(captions, str(response.main_topics))

    return {
        "topics": response.main_topics,
        "summary": summary,
    }
