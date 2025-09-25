from fastapi import APIRouter, HTTPException
from app.models.chatbot_model import ChatRequest, ChatResponse ,  YouTubeRequest, EmbeddingResponse
from app.services.rag_chatbot import build_chatbot
from langchain_core.messages import HumanMessage ,AIMessage , BaseMessage
from app.utils.utility_functions import load_transcript
from app.utils.rag_utility import text_splitter, generate_embeddings, save_embeddings_faiss, load_embeddings_faiss  

router = APIRouter(prefix="/chatbot", tags=["chatbot"])

@router.post("/create_embeddings", response_model=EmbeddingResponse)
def create_embeddings(request: YouTubeRequest):
    try:
        transcripts = load_transcript(request.youtube_url)
        print("loaded transcripts")
        chunks = text_splitter(transcripts)
        print("split into chunks")
        vector_store = generate_embeddings(chunks)
        print("generated embeddings")
        save_embeddings_faiss(request.thread_id, vector_store)
        print("saved embeddings")
        return EmbeddingResponse(message=f"✅ Embeddings created for thread {request.thread_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding error: {str(e)}")
    
@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        retriever = load_embeddings_faiss(request.thread_id)
        chatbot = build_chatbot(retriever)
        response = chatbot.invoke(
            {"messages": [HumanMessage(content=request.question)]},
            config={"configurable": {"thread_id": request.thread_id}}
        )
        chat_state = chatbot.get_state(
            config={"configurable": {"thread_id": request.thread_id}}
        )
        all_messages = chat_state.values["messages"]  # ✅ This returns list[BaseMessage]
        ai_message = response["messages"][-1].content

        #history_texts = [m.content for m in all_messages if isinstance(m, (HumanMessage, AIMessage))]
        return ChatResponse(answer=ai_message, message_history=all_messages)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot error: {str(e)}")