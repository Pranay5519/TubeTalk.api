from pydantic import BaseModel, Field 
from langchain_core.messages import HumanMessage ,AIMessage , BaseMessage
class AnsandTime(BaseModel):
    answer: list[str] = Field(description="Answers to user's question (no timestamps here) , Dont include code here")
    timestamps: float = Field(description="The time (in seconds) from where the answer was taken")
    code : str = Field(description="The code snippet related to the answer, if any" ,default=None)
    
# chat endpoint input schema
class ChatRequest(BaseModel):
    thread_id: str
    question: str

#chat endoints outoput schema
class ChatResponse(BaseModel):
    answer: str
    message_history : list[BaseMessage]

# create embeddings  input schema
class YouTubeRequest(BaseModel):
    thread_id: str
    youtube_url: str
# create embeddings  outupt schema
class EmbeddingResponse(BaseModel):
    message: str
    type : str
