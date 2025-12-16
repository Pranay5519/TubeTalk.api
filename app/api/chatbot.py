from fastapi import APIRouter, HTTPException,Depends
from app.pydantic_models.chatbot_model import ChatRequest, ChatResponse ,  YouTubeRequest, EmbeddingResponse
from app.services.chat_service import ChatbotService, ChatState
from typing import Annotated
from langchain_core.messages import HumanMessage ,AIMessage , BaseMessage
from app.utils.utility_functions import load_transcript
from app.utils.rag_utility import text_splitter, generate_embeddings, save_embeddings_faiss, load_embeddings_faiss  
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
        existing = load_embeddings_faiss(request.thread_id)
        if existing:
            return EmbeddingResponse(
                message=f"⚡ Embeddings already exist for thread {request.thread_id}",
                type="loaded"
            )
    except FileNotFoundError:
        try:
            # 2. Generate new embeddings if not found
            transcripts = load_transcript(request.youtube_url)
            print("loaded transcripts")

            chunks = text_splitter(transcripts)
            print("split into chunks")

            vector_store = generate_embeddings(chunks)
            print("generated embeddings")

            save_embeddings_faiss(request.thread_id, vector_store)
            print("saved embeddings")

            return EmbeddingResponse(
                message=f"✅ New embeddings created for thread {request.thread_id}",
                type="created"
            )

        except Exception as inner_error:
            raise HTTPException(
                status_code=500,
                detail=f"❌ Error while creating embeddings: {str(inner_error)}"
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"❌ Unexpected embedding error: {str(e)}"
        )
    
@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, api_key : str = Depends(get_gemini_api_key)):
    try:
        retriever = load_embeddings_faiss(request.thread_id)
        logger.info(f'loaded embeddings-{datetime.datetime.now()}')
        chatbot_service = ChatbotService(api_key=api_key)
        logger.info(f'chatbot service-{datetime.datetime.now()}')
        
        chatbot = chatbot_service.build_chatbot(retriever)
        response = chatbot.invoke(
            {"messages": [HumanMessage(content=request.question)]},
            config={"configurable": {"thread_id": request.thread_id}}
        )
        logger.info(f'response generated-{datetime.datetime.now()}')
        
        #chat_state = chatbot.get_state(
        #    config={"configurable": {"thread_id": request.thread_id}}
        #)
        all_messages = chatbot.get_state(config={'configurable': {'thread_id': request.thread_id}}).values['messages']
        ai_message = response["messages"][-1].content
        #print(response)
        #history_texts = [m.content for m in all_messages if isinstance(m, (HumanMessage, AIMessage))]
        return ChatResponse(answer=ai_message, message_history=all_messages)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot error: {str(e)}")
    

@router.post("/get_message_history", response_model=list[BaseMessage])
def get_history(thread_id : str, api_key: str = Depends(get_gemini_api_key)):
    retriever = load_embeddings_faiss(thread_id)
    chatbot_service = ChatbotService(api_key=api_key)
    chatbot = chatbot_service.build_chatbot(retriever)
    all_messages = chatbot.get_state(config={'configurable': {'thread_id': thread_id}}).values['messages']
    return all_messages 