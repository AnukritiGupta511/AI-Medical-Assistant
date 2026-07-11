from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Medical Assistant"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    POSTGRES_USER: str = "medical_user"
    POSTGRES_PASSWORD: str = "medical_password"
    POSTGRES_DB: str = "medical_db"
    # Fallback to local SQLite if Postgres isn't running
    DATABASE_URL: str = "sqlite:///./medical_assistant.db"
    
    REDIS_URL: str = "redis://localhost:6379/0"
    
    CHROMA_HOST: str = "chromadb"
    CHROMA_PORT: int = 8000
    
    SECRET_KEY: str = "your-super-secret-jwt-key-for-development"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    OPENAI_API_KEY: str = ""
    HUGGINGFACE_API_KEY: str = ""
    
    class Config:
        env_file = "../.env"
        case_sensitive = True

settings = Settings()
