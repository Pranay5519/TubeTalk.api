from pydantic import BaseModel, Field 
from langchain_core.messages import HumanMessage ,AIMessage , BaseMessage
class AnsandTime(BaseModel):
    answer: list[str] = Field(description="Answers to user's question (no timestamps here)")
    timestamps: float = Field(description="The time (in seconds) from where the answer was taken")
    code : str = Field(description="The code snippet related to the answer, if any" ,default=None)
    
from pydantic import BaseModel


class ChatRequest(BaseModel):
    thread_id: str
    question: str


class ChatResponse(BaseModel):
    answer: str
    message_history : list[BaseMessage]


class YouTubeRequest(BaseModel):
    thread_id: str
    youtube_url: str


class EmbeddingResponse(BaseModel):
    message: str
