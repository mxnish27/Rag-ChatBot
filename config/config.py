from pydantic_settings import BaseSettings
from typing import List, Optional
from pathlib import Path


class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "RAG Course Chatbot"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    
    # Vector Store Configuration
    VECTOR_STORE: str = "pinecone"
    
    # Pinecone Configuration
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None
    PINECONE_INDEX_NAME: str = "course-chatbot"
    
    # Chroma Configuration
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma_db"
    
    # LLM Configuration
    LLM_MODEL: str = "meta-llama/Llama-3-8B-Instruct"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 512
    LLM_TOP_P: float = 0.9
    
    # Embedding Model
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    
    # HuggingFace
    HUGGINGFACE_TOKEN: Optional[str] = None
    
    # Document Processing
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    MAX_DOCUMENTS: int = 1000
    
    # RAG Configuration
    RETRIEVAL_TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.7
    
    # Redis Cache
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # Security
    API_KEY_ENABLED: bool = False
    API_KEY: Optional[str] = None
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10485760
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx", ".txt", ".md"]
    
    # Data Directories
    DATA_DIR: str = "./data"
    DOCUMENTS_DIR: str = "./data/documents"
    UPLOADS_DIR: str = "./data/uploads"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def create_directories(self):
        """Create necessary directories if they don't exist"""
        Path(self.DATA_DIR).mkdir(parents=True, exist_ok=True)
        Path(self.DOCUMENTS_DIR).mkdir(parents=True, exist_ok=True)
        Path(self.UPLOADS_DIR).mkdir(parents=True, exist_ok=True)
        if self.VECTOR_STORE == "chroma":
            Path(self.CHROMA_PERSIST_DIRECTORY).mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.create_directories()
