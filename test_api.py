import requests

# -------------------------
# 1️⃣ Test /create_embeddings
# -------------------------
create_embeddings_url = "http://localhost:8000/chatbot/create_embeddings"

create_embeddings_payload = {
    "youtube_url": "https://youtu.be/yGWJo6a4g4w",
    "thread_id": "test_thread_1"
}

try:
    response = requests.post(create_embeddings_url, json=create_embeddings_payload)
    print("Create Embeddings Response:")
    print(response.json())
except Exception as e:
    print("Error calling create_embeddings:", e)

# -------------------------
# 2️⃣ Test /chat
# -------------------------
chat_url = "http://localhost:8000/chatbot/chat"

chat_payload = {
    "thread_id": "test_thread_1",
    "question": "Can you summarize the video?"
}

headers = {
    "gemini-api-key": "AIzaSyCuSbrEpqerOdAo4JVlZ3n7rr14mPMwRFM"  # your API key
}

try:
    response = requests.post(chat_url, json=chat_payload, headers=headers)
    print("\nChat Response:")
    print(response.json())
except Exception as e:
    print("Error calling chat:", e)
