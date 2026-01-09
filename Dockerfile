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
ARG CACHEBUST=3

# Install Python dependencies with fresh pip
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code and data
COPY src/ ./src/
COPY data/ ./data/
COPY scripts/ ./scripts/
COPY startup.py .

# Expose port (Railway will override with $PORT)
EXPOSE 8000

# Start via startup script (checks/rebuilds indices if needed)
CMD ["python", "startup.py"]

