FROM python:3.13.5-alpine3.22

WORKDIR /app

# 設定環境變數
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV GOOGLE_CLOUD_PROJECT=cloud-sre-poc-465509
ENV GOOGLE_CLOUD_LOCATION=asia-east1
ENV GOOGLE_GENAI_USE_VERTEXAI=true

# 安裝系統依賴
RUN apk add --no-cache \
    musl-dev \
    curl \
    ca-certificates

# 安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 複製專案檔案
COPY config.py .
COPY agent/ ./agent/

# 創建非 root 用戶 (GKE Autopilot 安全要求 - Alpine 版本)
RUN addgroup -g 1000 -S appuser \
    && adduser -u 1000 -S appuser -G appuser \
    && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 8080

# 啟動應用程式
CMD ["uvicorn", "agent.agent:a2a_app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]