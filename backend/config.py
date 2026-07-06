import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MODEL_NAME: str = "llama3.2"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    UPLOAD_DIR: str = "uploads"
    VECTOR_STORE_DIR: str = "vector_store"
    LOG_DIR: str = "logs"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    class Config:
        env_file = ".env"

settings = Settings()

for directory in [settings.UPLOAD_DIR, settings.VECTOR_STORE_DIR, settings.LOG_DIR]:
    os.makedirs(directory, exist_ok=True)