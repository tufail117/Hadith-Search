# Multi-stage Dockerfile: Build indices at Docker build time
# This ensures indices are built on Linux (same as Railway runtime)

# ============================================================
# Stage 1: Builder - Install dependencies and build indices
# ============================================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code and raw data for index building
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY raw_data/ ./raw_data/

# Create data directories
RUN mkdir -p data/processed data/index

# Build the search indices at BUILD TIME (on Linux!)
# This runs during 'docker build' and bakes indices into the image
RUN echo "========================================" && \
    echo "BUILDING SEARCH INDICES AT BUILD TIME" && \
    echo "========================================" && \
    python -m scripts.ingest && \
    echo "========================================" && \
    echo "INDEX BUILD COMPLETE" && \
    echo "========================================"

# ============================================================
# Stage 2: Runtime - Lean image with pre-built indices
# ============================================================
FROM python:3.11-slim

WORKDIR /app

# Install only runtime dependencies (no build tools needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY startup.py .

# Copy pre-built indices from builder stage (built on Linux!)
COPY --from=builder /app/data/index ./data/index
COPY --from=builder /app/data/processed ./data/processed

# Expose port (Railway will override with $PORT)
EXPOSE 8000

# Start the server directly - indices are already built!
CMD ["python", "startup.py"]
