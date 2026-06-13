# TerraPilot - Alibaba Cloud ECS Deployment
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Alibaba Cloud integration
COPY alicloud/ ./alicloud/
COPY src/ ./src/
COPY deploy/ ./deploy/

# Environment variables (set via ECS user-data or .env)
ENV PYTHONUNBUFFERED=1
ENV ALIBABA_CLOUD_ACCESS_KEY_ID=""
ENV ALIBABA_CLOUD_ACCESS_KEY_SECRET=""
ENV TABLESTORE_ENDPOINT=""
ENV SLS_ENDPOINT=""
ENV OSS_ENDPOINT=""
ENV QWEN_API_KEY=""

# Expose FastAPI port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]