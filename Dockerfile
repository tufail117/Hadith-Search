# Simple Dockerfile: Copy pre-built indices directly
# Indices are already built locally - no need to rebuild in Docker

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY startup.py .

# Copy pre-built indices (already built locally)
COPY data/processed/ ./data/processed/
COPY data/index/ ./data/index/

# Expose port (Railway will override with $PORT)
EXPOSE 8000

# Start the server - indices are pre-built!
CMD ["python", "startup.py"]
