from typing import Any, Protocol


class TelegramBotClient(Protocol):
    """Contrato mínimo usado pelo serviço de mensagens do Telegram."""

    async def send_photo(
        self, *, chat_id: str, photo_url: str, caption: str | None
    ) -> dict[str, Any]:
        """Envia uma foto e retorna o payload do Telegram."""
        ...

    async def edit_photo(
        self,
        *,
        chat_id: str,
        message_id: int,
        photo_url: str,
        caption: str | None,
    ) -> dict[str, Any]:
        """Edita uma foto e retorna o payload do Telegram."""
        ...
