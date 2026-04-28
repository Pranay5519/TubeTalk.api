import os
import re
import shutil
import sqlite3
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langsmith import traceable
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from app.cache.redis_cache import get_cache, set_cache
import logging

load_dotenv()
logger = logging.getLogger("uvicorn")

# ──────────────────────────────────────────────
# 1. Transcript Loader
# ──────────────────────────────────────────────
def load_transcript(url: str) -> str | None:
 
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11})'
    match = re.search(pattern, url)
    if match:
        video_id = match.group(1)
        try:
            captions = YouTubeTranscriptApi().fetch(video_id,languages=['en','hi']).snippets
            data = [f"{item.text} ({item.start})" for item in captions]
            return " ".join(data)
        except Exception as e:
            print(f"❌ Error fetching transcript for video {video_id}: {e}")
            return None


# ──────────────────────────────────────────────
# 2. Text Splitter
# ──────────────────────────────────────────────
def text_splitter(transcript: str):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.create_documents([transcript])

# ──────────────────────────────────────────────
# 3. Build Simple Cosine Similarity Retriever
# ──────────────────────────────────────────────
EMBEDDING_MODEL = "gemini-embedding-001"

def build_retriever(chunks, thread_id, api_key: str = None, *, top_n: int = 3, doc_language: str = "English"):
    import asyncio
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    effective_api_key = api_key or os.getenv("GOOGLE_API_KEY")
    
    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=effective_api_key
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=0,
        google_api_key=effective_api_key
    )

    base_dir = "faiss_indexes"
    index_path = os.path.join(base_dir, thread_id)
    cache_key = f"faiss_index:{thread_id}"

    def build_vector_store(docs):
        # 1. Try Redis cache first (serialized bytes)
        cached_data = get_cache(cache_key)
        if cached_data:
            logger.info(f"🚀 Loading FAISS index for {thread_id} from Redis cache")
            return FAISS.deserialize_from_bytes(
                cached_data, embeddings, allow_dangerous_deserialization=True
            ), "loaded_from_redis"

        # 2. Fallback to Disk
        if os.path.exists(index_path):
            logger.info(f"📁 Loading existing FAISS index from disk: {index_path}")
            vs = FAISS.load_local(
                index_path, embeddings, allow_dangerous_deserialization=True
            )
            # Store in Redis for next time
            try:
                set_cache(cache_key, vs.serialize_to_bytes())
                logger.info(f"✅ Cached {thread_id} to Redis")
            except Exception as e:
                logger.warning(f"⚠️ Failed to cache FAISS to Redis: {e}")
            return vs, "loaded_from_disk"
        else:
            if not docs:
                raise FileNotFoundError(f"❌ No FAISS index found for thread_id={thread_id}")
            logger.info("🧠 Requesting Gemini to create new embeddings...")
            vs = FAISS.from_documents(docs, embeddings)
            vs.save_local(index_path)
            # Store in Redis
            try:
                set_cache(cache_key, vs.serialize_to_bytes())
                logger.info(f"💾 FAISS index saved and cached: {thread_id}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to cache FAISS to Redis: {e}")
            return vs, "newly_created"

    vector_store, _ = build_vector_store(chunks)

    @traceable(name="simple-retriever", metadata={"embedding_model": EMBEDDING_MODEL, "index_path": index_path})
    def retrieve(query: str):
        search_query = query

        if doc_language.lower() == "hindi":
            print(f"🇮🇳 Hindi Document Detected: Optimizing query...")

            translation_prompt = ChatPromptTemplate.from_template(
                "Rewrite the following question into a single optimized search query in Hindi. "
                "Use transliteration for technical terms. Output ONLY the query.\n\n"
                "Original Question: {question}"
            )

            chain = translation_prompt | llm | StrOutputParser()

            # Use safety checks for the LLM response
            try:
                response = chain.invoke({"question": query}).strip()
                if response:
                    search_query = response
                    print(f"🔍 Optimized Hindi Query: {search_query}")
                else:
                    print("⚠️ LLM returned empty string. Falling back.")
            except Exception as e:
                print(f"⚠️ Translation failed: {e}. Using original query.")

        # Final Guardrail: Ensure search_query is NOT empty
        if not search_query or not search_query.strip():
            search_query = query

        docs = vector_store.similarity_search(search_query, k=top_n)
        return docs

    return retrieve

# ──────────────────────────────────────────────
# 4. One-shot pipeline helper 
# ──────────────────────────────────────────────
def create_retriever_from_url(youtube_url: str, doc_language: str, thread_id: str, api_key: str = None):
    """URL → transcript → chunks → retrieve callable"""

    logger.info("📥 Fetching transcript …")
    transcript = load_transcript(youtube_url)
    if not transcript:
        return None

    logger.info("✂️  Splitting into chunks …")
    chunks = text_splitter(transcript)

    logger.info(f"🔍 Building Cosine Similarity retriever ({doc_language}) …")
    retriever = build_retriever(chunks, thread_id=thread_id, api_key=api_key, doc_language=doc_language)

    logger.info("✅ Retriever ready.")
    return retriever 

# ──────────────────────────────────────────────
# FastAPI Helpers for backward compatibility
# ──────────────────────────────────────────────
def check_index_exists(thread_id: str) -> bool:
    base_dir = "faiss_indexes"
    index_path = os.path.join(base_dir, thread_id)
    return os.path.exists(index_path)

def load_existing_retriever(thread_id: str, api_key: str = None, doc_language: str = "English"):
    """
    Load an existing retriever for a thread_id.
    Redis caching is handled internally by build_retriever (caching vectors, not functions).
    """
    if not check_index_exists(thread_id):
        # We check disk existence first as a source of truth
        raise FileNotFoundError(f"❌ No FAISS index found for thread_id={thread_id}")
    
    # Just call build_retriever with None for docs; it will check Redis/Disk
    return build_retriever(None, thread_id=thread_id, api_key=api_key, doc_language=doc_language)

def clear_faiss_indexes(base_dir: str = "faiss_indexes"):
    if os.path.exists(base_dir):
        for item in os.listdir(base_dir):
            item_path = os.path.join(base_dir, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        print(f"✅ Cleared all contents inside: {base_dir}")
    
def delete_all_threads_from_db():
    try:
        conn = sqlite3.connect(r"tubetalk.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table_name in tables:
            cursor.execute(f"DELETE FROM {table_name[0]};")
        conn.commit()
        conn.close()
        print("✅ All threads deleted successfully.")
    except Exception as e:
        print("❌ Error while deleting threads:", e)
