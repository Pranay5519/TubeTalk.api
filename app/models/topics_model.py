from pydantic import BaseModel , Field
from typing import List, Optional

class Subtopic(BaseModel):
    subtopic: str = Field(description="Short name or description of the subtopic")
    #content: str = Field(description="Brief summary of the subtopic")
    timestamp: float = Field(description="Approx timestamp in seconds where this subtopic is discussed")
    importance: Optional[str] = Field(default=None, description="Optional importance: high/medium/low")

class MainTopic(BaseModel):
    topic: str = Field(description="Main topic name or short description")
    #content : str = Field(description="Brief summary of the main topic")
    timestamp: float = Field(description="Approx timestamp in seconds where the main topic starts")
    subtopics: List[Subtopic] = Field(description="List of subtopics under this main topic")

class TopicsOutput(BaseModel):
    main_topics: List[MainTopic] = Field(description="List of main topics with subtopics and timestamps")