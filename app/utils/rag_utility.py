import os
import shutil
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.cache.redis_cache import get_cache, set_cache
import logging
logger = logging.getLogger("uvicorn")
def text_splitter(transcript: str):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.create_documents([transcript])


def generate_embeddings(chunks):
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )
    return FAISS.from_documents(chunks, embeddings)


def retriever_docs(vector_store):
    return vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})


def save_embeddings_faiss(thread_id: str, vector_store, save_dir: str = "faiss_indexes"):
    """
    Save FAISS vector store locally for a given thread_id.
    """
    # Create the directory if it doesn't exist
    os.makedirs(save_dir, exist_ok=True)
    # Build the save path
    save_path = os.path.join(save_dir, thread_id)
    # Save the vector store
    vector_store.save_local(save_path)
    print(f"✅ Embeddings for {thread_id} saved at {save_path}")


def load_embeddings_faiss(thread_id: str, save_dir: str = "faiss_indexes"):
    cache_key = f"retriever:{thread_id}"

    retriever = get_cache(cache_key)
    if retriever:
        logger.info(f"⚡ Retriever for {thread_id} loaded from Redis cache")
        #print(f"⚡ Retriever for {thread_id} loaded from Redis cache")
        return retriever

    load_path = os.path.join(save_dir, thread_id)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )

    if os.path.exists(load_path):
        vector_store = FAISS.load_local(
            load_path, embeddings, allow_dangerous_deserialization=True
        )
        retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        set_cache(cache_key, retriever)
        logger.info(f"✅ Cached retriever for {thread_id}")
        return retriever
    else:
        raise FileNotFoundError(f"❌ No FAISS index found for thread_id={thread_id}")

def clear_faiss_indexes(base_dir: str = "faiss_indexes"):
    if os.path.exists(base_dir):
        for item in os.listdir(base_dir):
            item_path = os.path.join(base_dir, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        print(f"✅ Cleared all contents inside: {base_dir}")