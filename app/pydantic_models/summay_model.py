from pydantic import BaseModel, Field
from typing import List, Optional
from app.pydantic_models.topics_model import TopicsOutput


class SubtopicSummary(BaseModel):
    subtopic: str = Field(description="The subtopic being summarized")
    summary: str = Field(description="Concise summary of the subtopic")
    timestamp: float = Field(description="Timestamp where this subtopic is discussed")
    importance: Optional[str] = Field(default=None, description="Importance level: high/medium/low")


class TopicSummary(BaseModel):
    topic: str = Field(description="Main topic being summarized")
    summary: str = Field(description="Concise summary of the topic")
    timestamp: float = Field(description="Timestamp where this topic is discussed")
    subtopics: List[SubtopicSummary] = Field(description="Summaries of subtopics under this topic")

class SummaryOutput(BaseModel):
    main_summary: List[TopicSummary] = Field(description="Summaries of all main topics with their subtopics")


class CombinedStudyOutput(BaseModel):
    topics: TopicsOutput = Field(description="List of main topics and subtopics with timestamps")
    summary: SummaryOutput = Field(description="Detailed summaries for each topic/subtopic")
