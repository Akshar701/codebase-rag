# ============================================
# Production Dockerfile for FastAPI Backend
# ============================================

FROM python:3.10-slim

WORKDIR /app

# Install system dependencies if needed (compiler, git, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy backend codebase
COPY app/ app/

# Expose port (Render/Railway/Fly.io dynamically injects PORT env variable)
EXPOSE 8000

# Command to run uvicorn
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
