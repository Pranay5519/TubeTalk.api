from fastapi import FastAPI
from app.api import topics, summary, quiz, chatbot , url , get_thread_id , delete_threads
from app.middleware.logging_middleware import LoggingMiddleware
import logging

# ----------------------------
# Logging setup
# ----------------------------
# Configure root logger (optional, in case some library logs to root)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Configure uvicorn loggers
uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_logger.setLevel(logging.INFO)

uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.setLevel(logging.INFO)

# ----------------------------
# Create FastAPI app
# ----------------------------
app = FastAPI(
    title="TubeTalk.ai API",
    description="API for Quiz Generator, Summary Generator, RAG Chatbot, and Topics Generator",
    version="1.0.0"
)

# ----------------------------
# Add logging middleware
# ----------------------------
app.add_middleware(LoggingMiddleware)

# ----------------------------
# Include routers
# ----------------------------
app.include_router(topics.router, tags=["topics"])
app.include_router(summary.router, tags=["summary"])
app.include_router(quiz.router, tags=["quiz"])
app.include_router(chatbot.router, tags=["chatbot"])
app.include_router(url.router , tags=['url'])
app.include_router(get_thread_id.router , tags=['thread_ids'])
app.include_router(delete_threads.router , tags=['del_threads'])

@app.get("/")
def root():
    return {"message": "Welcome to TubeTalk.ai API!"}