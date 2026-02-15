# ActionMind AI - Todo AI Chatbot Backend
# Multi-stage Docker build for optimized image size

# Stage 1: Builder - Install dependencies
FROM python:3.13-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runner - Minimal production image
FROM python:3.13-slim

WORKDIR /app

# Install runtime dependencies only (no build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security BEFORE copying files
RUN groupadd -r appuser && useradd -r -g appuser -u 1000 appuser

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code with proper ownership
COPY --chown=appuser:appuser ./src ./src
COPY --chown=appuser:appuser .env.template .env.template

# Switch to non-root user
USER appuser

# Expose FastAPI port
EXPOSE 8000

# Health check endpoint - optimized for Kubernetes
# Give enough time for app to start (database init, MCP server, etc.)
HEALTHCHECK --interval=30s --timeout=10s --start-period=50s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=5)" || exit 1

# Run FastAPI application with uvicorn (set PYTHONPATH to find src module)
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
# Graceful shutdown - handle SIGTERM
STOPSIGNAL SIGTERM
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--loop", "uvloop", "--log-config", "null"]
