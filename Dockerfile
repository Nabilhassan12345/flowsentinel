# ============================================================================
# FlowSentinel Backend - Multi-Stage Docker Build
# ============================================================================
# This Dockerfile uses multi-stage builds to create a smaller, more secure
# production image by separating the build dependencies from the runtime.
# ============================================================================

# ----------------------------------------------------------------------------
# Stage 1: Builder - Install dependencies
# ----------------------------------------------------------------------------
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies to a local directory
RUN pip install --no-cache-dir --user -r requirements.txt

# ----------------------------------------------------------------------------
# Stage 2: Runtime - Create final lightweight image
# ----------------------------------------------------------------------------
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/root/.local/bin:$PATH

# Create app directory
WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder /root/.local /root/.local

# Copy application files
COPY src/main.py ./src/
COPY tests/demo.py tests/test_api.py ./tests/
COPY .env.example .

# Create a non-root user for security
RUN useradd -m -u 1000 flowsentinel && \
    chown -R flowsentinel:flowsentinel /app

# Switch to non-root user
USER flowsentinel

# Expose port 8000
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=3)"

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
