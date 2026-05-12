from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.telegram_message import TelegramMessage


class TelegramMessageRepository:
    """Repositório assíncrono para mensagens do Telegram."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_reference(self, reference: str) -> TelegramMessage | None:
        """Busca uma mensagem salva por referência de negócio."""
        result = await self.session.execute(
            select(TelegramMessage).where(TelegramMessage.reference == reference)
        )
        return result.scalar_one_or_none()

    async def save_sent_message(
        self,
        *,
        reference: str,
        chat_id: str,
        message_id: int,
        media_type: str = "photo",
        caption: str | None = None,
    ) -> TelegramMessage:
        """Salva ou atualiza o identificador da mensagem enviada."""
        message = await self.get_by_reference(reference)
        if message is None:
            message = TelegramMessage(reference=reference, chat_id=chat_id, message_id=message_id)
            self.session.add(message)

        message.chat_id = chat_id
        message.message_id = message_id
        message.media_type = media_type
        message.caption = caption
        await self.session.flush()
        return message
