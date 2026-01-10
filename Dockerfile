# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Force cache bust (change this value to force rebuild)
ARG CACHEBUST=4

# Install Python dependencies with fresh pip
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code and data
COPY src/ ./src/
COPY data/ ./data/
COPY scripts/ ./scripts/
COPY startup.py .

# Rebuild indices during build (ensures cross-platform compatibility)
# This runs the ingestion to create fresh ChromaDB and BM25 indices
RUN python -c "from src.ingestion.indexer import build_all_indices; build_all_indices()"

# Expose port (Railway will override with $PORT)
EXPOSE 8000

# Start the application directly (indices are pre-built)
CMD ["sh", "-c", "python -m uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

