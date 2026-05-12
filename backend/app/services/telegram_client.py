from typing import Any

import httpx


class TelegramClientError(RuntimeError):
    """Erro retornado pela API HTTP do Telegram."""


class TelegramClient:
    """Cliente mínimo para envio e edição de mídia no Telegram Bot API."""

    def __init__(
        self, *, bot_token: str, api_base_url: str, http_client: httpx.AsyncClient
    ) -> None:
        self.bot_token = bot_token
        self.api_base_url = api_base_url.rstrip("/")
        self.http_client = http_client

    async def send_photo(
        self, *, chat_id: str, photo_url: str, caption: str | None
    ) -> dict[str, Any]:
        """Envia uma foto para um chat, grupo ou canal."""
        return await self._post(
            "sendPhoto",
            json={"chat_id": chat_id, "photo": photo_url, "caption": caption},
        )

    async def edit_photo(
        self,
        *,
        chat_id: str,
        message_id: int,
        photo_url: str,
        caption: str | None,
    ) -> dict[str, Any]:
        """Edita a foto de uma mensagem enviada anteriormente."""
        return await self._post(
            "editMessageMedia",
            json={
                "chat_id": chat_id,
                "message_id": message_id,
                "media": {"type": "photo", "media": photo_url, "caption": caption},
            },
        )

    async def _post(self, method: str, *, json: dict[str, Any]) -> dict[str, Any]:
        """Executa uma chamada POST e valida o envelope padrão do Telegram."""
        if not self.bot_token:
            raise TelegramClientError("Telegram bot token is not configured.")

        response = await self.http_client.post(
            f"{self.api_base_url}/bot{self.bot_token}/{method}",
            json=json,
            timeout=20,
        )
        data = response.json()
        if response.is_error or data.get("ok") is not True:
            description = data.get("description", "Telegram API request failed.")
            raise TelegramClientError(description)
        return data
