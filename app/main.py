from fastapi import FastAPI
from app.api import topics

app = FastAPI(
    title="TubeTalk.ai API",
    description="API for Quiz Generator, Summary Generator, RAG Chatbot, and Topics Generator",
    version="1.0.0"
)
app.include_router(topics.router,tags=["topics"])