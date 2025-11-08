🚀 TubeTalk.ai API

TubeTalk.ai is a FastAPI-based backend that powers multiple AI services including:

RAG-based Chatbot

Quiz Generator

Summary Generator

Topic Extractor

It is modular, production-ready, and includes caching, logging middleware, and clean service architecture.

🧩 Project Structure
app/
│
├── main.py                     # FastAPI app entry point
│
├── api/                        # All API route definitions
│   ├── chatbot.py
│   ├── quiz.py
│   ├── summary.py
│   ├── topics.py
│   ├── __init__.py
│
├── cache/                      # Redis caching utilities
│   └── redis_cache.py
│
├── core/                       # Core logic (auth, config, etc.)
│   ├── auth.py
│   ├── __init__.py
│
├── database/                   # Database models, CRUD logic
│   ├── crud.py
│   ├── database.py
│   ├── models.py
│   ├── __init__.py
│
├── middleware/                 # Custom middleware
│   ├── logging_middleware.py
│   ├── __init__.py
│
├── pydantic_models/            # Pydantic schemas for validation
│   ├── chatbot_model.py
│   ├── quiz_model.py
│   ├── summary_model.py
│   ├── topics_model.py
│   ├── __init__.py
│
├── services/                   # Business logic for each module
│   ├── chat_service.py
│   ├── quiz_service.py
│   ├── summary_service.py
│   ├── topics_service.py
│   ├── __init__.py
│
└── utils/                      # Helper and utility functions
    ├── rag_utility.py
    ├── utility_functions.py
    ├── __init__.py

⚙️ Setup Instructions
1. Clone the Repository
git clone https://github.com/<your-username>/tubetalk-ai-api.git
cd tubetalk-ai-api

2. Create a Virtual Environment
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

3. Install Dependencies
pip install -r requirements.txt

4. Run Redis (for caching)

You can use Docker or a local Redis server:

docker run -d -p 6379:6379 redis

5. Start the FastAPI App
uvicorn app.main:app --reload

6. Visit the Docs

Interactive Swagger UI: 👉 http://localhost:8000/docs

ReDoc Documentation: 👉 http://localhost:8000/redoc

🌐 API Endpoints
🧠 Chatbot

Base URL: /chatbot

Method	Endpoint	Description
POST	/chatbot/query	Send a query to the RAG-based chatbot and receive a contextual answer.
📝 Summary Generator

Base URL: /summary

Method	Endpoint	Description
POST	/summary/generate	Generate a summarized version of provided content.
🎯 Quiz Generator

Base URL: /quiz

Method	Endpoint	Description
POST	/quiz/generate	Generate a quiz based on text, topics, or video transcript.
GET	/quiz/{quiz_id}	Retrieve details of a specific quiz.
📚 Topic Generator

Base URL: /topics

Method	Endpoint	Description
POST	/topics/generate	Extract key topics or concepts from text or transcript.
🧩 Utility Endpoints
Method	Endpoint	Description
GET	/url/fetch	Fetch data from given URL (RAG use-case).
GET	/thread_id/get	Retrieve a unique thread/session ID.
DELETE	/thread_id/delete	Delete a thread from cache or memory.
🧠 Middleware

LoggingMiddleware → Logs all incoming requests and responses with timestamps and status codes.

🗄️ Caching

Uses Redis for storing chatbot context, RAG retrieval cache, and quiz data for faster performance.

📦 Docker Setup (Optional)

You can run the app inside Docker:

docker build -t tubetalk-ai-api .
docker run -d -p 8000:8000 --name tubetalk-api tubetalk-ai-api

🧑‍💻 Developer Notes

Python: >=3.9

Framework: FastAPI

Caching: Redis

Logging: Custom middleware + Uvicorn logs

Future plans: Authentication, API rate limiting, and analytics dashboard

❤️ Author

Pranay
Student AI Engineer | Machine Learning Enthusiast
GitHub: @pranay5519