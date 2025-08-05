import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Google ADK Configuration
    GOOGLE_GENAI_USE_VERTEXAI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "TRUE")
    GOOGLE_ADK_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "your-project-id")
    GOOGLE_ADK_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    GOOGLE_ADK_AGENT_ID = os.getenv("GOOGLE_ADK_AGENT_ID", "graylog-query-planner")
    
    # # AI Configuration
    # GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY")
    GOOGLE_AI_MODEL = os.getenv("GOOGLE_AI_MODEL", "gemini-2.0-flash")
    
    # Service Configuration
    SERVICE_HOST = os.getenv("SERVICE_HOST", "0.0.0.0")
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8000"))
    
    # Graylog Configuration
    GRAYLOG_SERVER_URL = os.getenv("GRAYLOG_SERVER_URL", "http://localhost:9000")
    GRAYLOG_API_TOKEN = os.getenv("GRAYLOG_API_TOKEN")
    
    # A2A Communication Configuration
    A2A_ENDPOINT = os.getenv("A2A_ENDPOINT", "/api/v1/a2a")
    A2A_SECRET_KEY = os.getenv("A2A_SECRET_KEY", "your-secret-key")
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO") 