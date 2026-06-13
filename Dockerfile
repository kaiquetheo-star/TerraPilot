# TerraPilot - Alibaba Cloud ECS Deployment
FROM python:3.12-slim

WORKDIR /app

# Runtime tools include curl so Docker HEALTHCHECK can call /health.
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY alicloud/ ./alicloud/
COPY deploy/ ./deploy/
COPY src/ ./src/

ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production
ENV LOG_LEVEL=INFO
ENV ECS_REGION=ap-southeast-1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
