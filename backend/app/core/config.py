from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação carregadas por variáveis de ambiente."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "FastAPI Telegram Base"
    environment: str = "local"
    database_url: str = Field(
        default="postgresql+asyncpg://app:app@localhost:5432/app",
        validation_alias="DATABASE_URL",
    )
    telegram_bot_token: str = Field(default="", validation_alias="TELEGRAM_BOT_TOKEN")
    telegram_webhook_secret: str = Field(
        default="local-secret", validation_alias="TELEGRAM_WEBHOOK_SECRET"
    )
    telegram_api_base_url: str = Field(
        default="https://api.telegram.org",
        validation_alias="TELEGRAM_API_BASE_URL",
    )

    @property
    def telegram_webhook_path(self) -> str:
        """Retorna o caminho interno do webhook do Telegram."""
        return f"/telegram/webhook/{self.telegram_webhook_secret}"


@lru_cache
def get_settings() -> Settings:
    """Cria uma instância cacheada das configurações."""
    return Settings()
