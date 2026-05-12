from collections.abc import AsyncGenerator

import httpx
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_session
from app.repositories.telegram_message_repository import TelegramMessageRepository
from app.services.telegram_client import TelegramClient
from app.services.telegram_message_service import TelegramMessageService


def get_http_client(request: Request) -> httpx.AsyncClient:
    """Obtém o cliente HTTP compartilhado no lifespan."""
    return request.app.state.http_client


def get_telegram_client(
    http_client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
) -> TelegramClient:
    """Cria um cliente do Telegram para a requisição atual."""
    return TelegramClient(
        bot_token=settings.telegram_bot_token,
        api_base_url=settings.telegram_api_base_url,
        http_client=http_client,
    )


async def get_telegram_message_service(
    session: AsyncSession = Depends(get_session),
    client: TelegramClient = Depends(get_telegram_client),
) -> AsyncGenerator[TelegramMessageService]:
    """Fornece o serviço de mensagens com commit automático."""
    repository = TelegramMessageRepository(session)
    yield TelegramMessageService(client=client, repository=repository)
    await session.commit()
