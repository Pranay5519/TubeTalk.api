from fastapi import FastAPI
from app.api import topics,summary,quiz,chatbot
# uvicorn app.main:app --reload
import logging
from app.middleware.logging_middleware import LoggingMiddleware


app = FastAPI(
    title="TubeTalk.ai API",
    description="API for Quiz Generator, Summary Generator, RAG Chatbot, and Topics Generator",
    version="1.0.0"
)
#linking middleware to app
logging.basicConfig(
    level=logging.INFO,  # Set minimum level to INFO
    format="%(asctime)s - %(levelname)s - %(message)s"
)
app.add_middleware(LoggingMiddleware)

app.include_router(topics.router,tags=["topics"])
app.include_router(summary.router,tags=["summary"])
app.include_router(quiz.router,tags=["quiz"])
app.include_router(chatbot.router,tags=["chatbot"])
