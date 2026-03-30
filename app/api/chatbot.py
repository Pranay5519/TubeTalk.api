from fastapi import APIRouter, HTTPException,Depends
from app.pydantic_models.chatbot_model import ChatRequest, ChatResponse ,  YouTubeRequest, EmbeddingResponse
from app.services.chat_service import ChatbotService, ChatState
from typing import Annotated
from langchain_core.messages import HumanMessage ,AIMessage , BaseMessage
from app.utils.rag_utility import text_splitter, check_index_exists, load_existing_retriever, create_retriever_from_url
from app.core.auth import get_gemini_api_key
from fastapi.concurrency import run_in_threadpool
import logging
from app.database.crud import save_url_to_db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.database.database import Base, engine, SessionLocal
import datetime

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
logger = logging.getLogger("uvicorn")
router = APIRouter(prefix="/chatbot", tags=["chatbot"]) 

# create-embeddings       
@router.post("/create_embeddings", response_model=EmbeddingResponse)
async def create_embeddings(
    request: YouTubeRequest,
    db: Session = Depends(get_db)
):
    """
    Create or load FAISS embeddings for a given YouTube transcript and thread_id.
    """
    try:
        try:
            logger.info("Saving url to Db")
            await run_in_threadpool(save_url_to_db, db, request.thread_id, request.youtube_url)
        except SQLAlchemyError as db_error:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
            
        # 1. Check if embeddings already exist for this thread_id
        is_existing = await run_in_threadpool(check_index_exists, request.thread_id)
        if is_existing:
            return EmbeddingResponse(
                message=f"⚡ Embeddings already exist for thread {request.thread_id}",
                type="loaded"
            )
            
        # 2. Generate new embeddings if not found
        retriever = await run_in_threadpool(
            create_retriever_from_url,
            request.youtube_url, 
            "English", 
            request.thread_id
        )
        
        if not retriever:
            raise HTTPException(
                status_code=400,
                detail="❌ Failed to create embeddings. Transcript might be empty or invalid."
            )

        return EmbeddingResponse(
            message=f"✅ New embeddings created for thread {request.thread_id}",
            type="created"
        )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"❌ Unexpected embedding error: {str(e)}"
        )

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, api_key : str = Depends(get_gemini_api_key)):
    import asyncio
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
        
    try:
        retriever = load_existing_retriever(request.thread_id)
        logger.info(f'loaded embeddings-{datetime.datetime.now()}')
       
        chatbot_service = ChatbotService(api_key=api_key)
        logger.info(f'chatbot service-{datetime.datetime.now()}')
        
        chatbot = chatbot_service.build_chatbot(retriever)
        response = chatbot.invoke(
            {"messages": [HumanMessage(content=request.question)]},
            config={"configurable": {"thread_id": request.thread_id}}
        )
        logger.info(f'response generated-{datetime.datetime.now()}')
        
        all_messages = chatbot.get_state(config={'configurable': {'thread_id': request.thread_id}}).values['messages']
        ai_message = response["messages"][-1].content
        
        return ChatResponse(answer=ai_message, message_history=all_messages)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot error: {str(e)}")
    
# testing purpose
@router.post("/get_message_history", response_model=list[BaseMessage])
def get_history(thread_id : str, api_key: str = Depends(get_gemini_api_key)):
    import asyncio
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    try:
        retriever = load_existing_retriever(thread_id)
        chatbot_service = ChatbotService(api_key=api_key)
        chatbot = chatbot_service.build_chatbot(retriever)
        all_messages = chatbot.get_state(config={'configurable': {'thread_id': thread_id}}).values['messages']
        return all_messages 
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot error: {str(e)}")