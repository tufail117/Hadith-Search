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
ARG CACHEBUST=2

# Install Python dependencies with fresh pip
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code and data
COPY src/ ./src/
COPY data/ ./data/
COPY scripts/ ./scripts/

# Expose port (Railway will override with $PORT)
EXPOSE 8000

# Start the application
CMD ["sh", "-c", "python -m uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
