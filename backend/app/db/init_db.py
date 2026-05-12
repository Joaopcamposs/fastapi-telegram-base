import asyncio

from app.db.base import Base
from app.db.session import engine
from app.models.telegram_message import TelegramMessage

__all__ = ["TelegramMessage"]


async def init_db() -> None:
    """Cria as tabelas necessárias para desenvolvimento local."""
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(init_db())
