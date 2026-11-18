from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação, lidas de variáveis de ambiente ou do arquivo .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Assistente de Suporte de TI"
    environment: str = "development"
    cors_origins: list[str] = ["http://localhost:5173"]

    chunk_size: int = 800
    chunk_overlap: int = 150


@lru_cache
def get_settings() -> Settings:
    return Settings()
