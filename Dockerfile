# Use a lightweight Python base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for faiss, dvc, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy necessary application files only
COPY app/ ./app/
COPY tubetalk.db .

# (Optional: Copy other static assets/folders if your app needs them)

# Expose app port
EXPOSE 8000

# Run FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
