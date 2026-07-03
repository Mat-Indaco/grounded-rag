"""Configuración centralizada, leída de variables de entorno (.env)."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Busca .env en la raíz del repo y en apps/api. extra="ignore" para no romper
    # si el .env tiene además claves del frontend.
    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    anthropic_api_key: str
    voyage_api_key: str
    supabase_url: str
    supabase_service_key: str

    gen_model: str = "claude-opus-4-8"
    judge_model: str = "claude-haiku-4-5"
    embed_model: str = "voyage-3.5"
    embed_dim: int = 1024

    top_k: int = 5

    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
