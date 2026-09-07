from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ProcureOps"
    app_env: str = "development"
    debug: bool = True
    HOST: str = "0.0.0.0"   # Docker port
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    database_url: str

    REDIS_URL: str
    HF_TOKEN: str

    CORS_ORIGINS: str

    groq_api_key: str
    groq_model: str
    groq_temperature: float = 0.1  # with default value
    groq_timeout: int = 30  # with default value

    CHROMA_PERSIST_DIRECTORY: str = "/app/data/chroma_db"
    CHROMA_COLLECTION_NAME: str = "procureops_knowledge_base"

    LANGGRAPH_STRICT_MSGPACK: str = "false"
    LANGSMITH_TRACING: str
    LANGSMITH_API_KEY: str
    LANGSMITH_PROJECT: str
    LANGSMITH_ENDPOINT: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()