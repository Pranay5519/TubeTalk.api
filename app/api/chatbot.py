from fastapi import APIRouter, HTTPException,Depends
from app.pydantic_models.chatbot_model import ChatRequest, ChatResponse ,  YouTubeRequest, EmbeddingResponse
from app.services.chat_service import ChatbotService, ChatState
from typing import Annotated
from langchain_core.messages import HumanMessage ,AIMessage , BaseMessage
from app.utils.utility_functions import load_transcript
from app.utils.rag_utility import text_splitter, generate_embeddings, save_embeddings_faiss, load_embeddings_faiss  
from app.core.auth import get_gemini_api_key
import logging
logger = logging.getLogger("uvicorn")
router = APIRouter(prefix="/chatbot", tags=["chatbot"])

@router.post("/create_embeddings", response_model=EmbeddingResponse)
def create_embeddings(request: YouTubeRequest):
    try:
        # 1. Try loading existing embeddings safely
        try:
            existing = load_embeddings_faiss(request.thread_id)
            logger.info(f"Loaded saved Embeddings {request.thread_id}")
        except FileNotFoundError:
            existing = None
        except Exception:
            existing = None

        if existing:
            return EmbeddingResponse(
                message=f"⚡ Embeddings already exist for thread {request.thread_id}"
            )
        
        # 2. Generate new embeddings if not found
        transcripts = load_transcript(request.youtube_url)
        if not transcripts:
            raise HTTPException(status_code=404, detail="Transcript not found")

        print("loaded transcripts")
        chunks = text_splitter(transcripts)
        print("split into chunks")
        vector_store = generate_embeddings(chunks)
        print("generated embeddings")
        save_embeddings_faiss(request.thread_id, vector_store)
        print("saved embeddings")

        return EmbeddingResponse(
            message=f"✅ Embeddings created for thread {request.thread_id}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding error: {str(e)}")
    
@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, api_key : str = Depends(get_gemini_api_key)):
    try:
        retriever = load_embeddings_faiss(request.thread_id)
        chatbot_service = ChatbotService(api_key=api_key)
        chatbot = chatbot_service.build_chatbot(retriever)
        response = chatbot.invoke(
            {"messages": [HumanMessage(content=request.question)]},
            config={"configurable": {"thread_id": request.thread_id}}
        )
        chat_state = chatbot.get_state(
            config={"configurable": {"thread_id": request.thread_id}}
        )
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