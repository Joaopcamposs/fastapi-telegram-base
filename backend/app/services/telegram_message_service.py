from app.repositories.telegram_message_repository import TelegramMessageRepository
from app.schemas.telegram import EditPhotoRequest, SendPhotoRequest, TelegramMessageResponse
from app.services.telegram_protocol import TelegramBotClient


class MessageNotFoundError(LookupError):
    """Erro usado quando uma referência não possui mensagem salva."""


class TelegramMessageService:
    """Orquestra envio, edição e persistência de mensagens do Telegram."""

    def __init__(self, *, client: TelegramBotClient, repository: TelegramMessageRepository) -> None:
        self.client = client
        self.repository = repository

    async def send_photo(self, request: SendPhotoRequest) -> TelegramMessageResponse:
        """Envia uma foto e guarda o ID para permitir edição posterior."""
        payload = await self.client.send_photo(
            chat_id=request.chat_id,
            photo_url=request.photo_url,
            caption=request.caption,
        )
        result = payload["result"]
        message = await self.repository.save_sent_message(
            reference=request.reference,
            chat_id=str(result["chat"]["id"]),
            message_id=int(result["message_id"]),
            media_type="photo",
            caption=request.caption,
        )
        return TelegramMessageResponse.model_validate(message, from_attributes=True)

    async def edit_photo(
        self, reference: str, request: EditPhotoRequest
    ) -> TelegramMessageResponse:
        """Edita uma foto usando o ID de mensagem salvo no banco."""
        message = await self.repository.get_by_reference(reference)
        if message is None:
            raise MessageNotFoundError(f"Message reference '{reference}' was not found.")

        await self.client.edit_photo(
            chat_id=message.chat_id,
            message_id=message.message_id,
            photo_url=request.photo_url,
            caption=request.caption,
        )
        message.caption = request.caption
        await self.repository.session.flush()
        return TelegramMessageResponse.model_validate(message, from_attributes=True)
