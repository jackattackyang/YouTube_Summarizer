FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create directory for HuggingFace cache
ENV HF_HOME=/app/.cache/huggingface
RUN mkdir -p $HF_HOME

# Copy the rest of the application
COPY . .

# Download and cache the model during build
RUN python -c "from langchain_community.embeddings import HuggingFaceEmbeddings; HuggingFaceEmbeddings(model_name='sentence-transformers/all-mpnet-base-v2')"

# Default port if not set by Heroku
ENV PORT=5001

# Run the application
CMD uvicorn api.app:app --host 0.0.0.0 --port $PORT 