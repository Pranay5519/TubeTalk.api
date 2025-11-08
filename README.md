<div align="center">

# 🚀 TubeTalk.ai API

**A FastAPI-based backend powering multiple AI services**

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

[Features](#-features) •
[Installation](#️-installation) •
[API Documentation](#-api-endpoints) •
[Docker Setup](#-docker-setup)

</div>

---

## 📋 Overview

TubeTalk.ai is a modular, production-ready FastAPI backend that provides:

- 🤖 **RAG-based Chatbot** - Contextual conversations powered by retrieval-augmented generation
- 📝 **Quiz Generator** - Generate quizzes from text, topics, or video transcripts
- 📊 **Summary Generator** - Intelligent content summarization
- 🎯 **Topic Extractor** - Extract key concepts and topics from content

Built with clean architecture, Redis caching, and comprehensive logging middleware.

---

## 🏗️ Project Structure
```
app/
│
├── main.py                     # FastAPI app entry point
│
├── api/                        # All API route definitions
│   ├── chatbot.py
│   ├── quiz.py
│   ├── summary.py
│   ├── topics.py
│   └── __init__.py
│
├── cache/                      # Redis caching utilities
│   └── redis_cache.py
│
├── core/                       # Core logic (auth, config, etc.)
│   ├── auth.py
│   └── __init__.py
│
├── database/                   # Database models, CRUD logic
│   ├── crud.py
│   ├── database.py
│   ├── models.py
│   └── __init__.py
│
├── middleware/                 # Custom middleware
│   ├── logging_middleware.py
│   └── __init__.py
│
├── pydantic_models/            # Pydantic schemas for validation
│   ├── chatbot_model.py
│   ├── quiz_model.py
│   ├── summary_model.py
│   ├── topics_model.py
│   └── __init__.py
│
├── services/                   # Business logic for each module
│   ├── chat_service.py
│   ├── quiz_service.py
│   ├── summary_service.py
│   ├── topics_service.py
│   └── __init__.py
│
└── utils/                      # Helper and utility functions
    ├── rag_utility.py
    ├── utility_functions.py
    └── __init__.py
```

---

## ⚙️ Installation

### Prerequisites

- Python 3.9+
- Redis (optional, for caching)
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/tubetalk-ai-api.git
cd tubetalk-ai-api
```

### 2. Create a Virtual Environment

**Mac/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Redis (Optional)

**Using Docker:**
```bash
docker run -d -p 6379:6379 redis
```

**Or use a local Redis server**

### 5. Start the Application
```bash
uvicorn app.main:app --reload
```

### 6. Access API Documentation

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs) 📖
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc) 📚

---

## 🌐 API Endpoints

### 🧠 Chatbot

**Base URL:** `/chatbot`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/chatbot/chat` | Send a query to the RAG-based chatbot and receive a contextual answer |

---

### 📝 Summary Generator

**Base URL:** `/summary`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/summary/get_summary` | Generate a summarized version of provided content |

---

### 🎯 Quiz Generator

**Base URL:** `/quiz`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/quiz/generate_quiz` | Generate a quiz based on text, topics, or video transcript |


---

### 📚 Topic Generator

**Base URL:** `/topics`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/topics/get_topics` | Extract key topics or concepts from text or transcript |

---

### 🛠️ Utility Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/url/fetch` | Fetch data from given URL (RAG use-case) |
| `GET` | `/thread_id/get` | Retrieve a unique thread/session ID |
| `DELETE` | `/thread_id/delete` | Delete a thread from cache or memory |

---

## 🔧 Features

### 🧩 Middleware

- **LoggingMiddleware** - Logs all incoming requests and responses with timestamps and status codes

### 🗄️ Caching

- **Redis Integration** - Stores chatbot context, RAG retrieval cache, and quiz data for enhanced performance

### 🏛️ Architecture

- Clean, modular structure following best practices
- Separation of concerns (routes, services, models)
- Pydantic validation for request/response schemas
- Production-ready with comprehensive error handling

---

## 🐳 Docker Setup

Run the application in a containerized environment:

### Build the Image
```bash
docker build -t tubetalk-ai-api .
```

### Run the Container
```bash
docker run -d -p 8000:8000 --name tubetalk-api tubetalk-ai-api
```

### Docker Compose (if available)
```bash
docker-compose up -d
```

---

## 🧑‍💻 Developer Notes

- **Python:** >=3.9
- **Framework:** FastAPI
- **Caching:** Redis
- **Logging:** Custom middleware + Uvicorn logs
- **Future Plans:**
  - 🔐 Authentication & Authorization
  - ⏱️ API Rate Limiting
  - 📊 Analytics Dashboard
  - 🧪 Comprehensive Test Suite

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📬 Contact

**Pranay**  
Student AI Engineer | Machine Learning Enthusiast

[![GitHub](https://img.shields.io/badge/GitHub-@pranay5519-181717?style=for-the-badge&logo=github)](https://github.com/pranay5519)

---

<div align="center">

Made with ❤️ by [Pranay](https://github.com/pranay5519)

⭐ Star this repo if you find it useful!

</div>