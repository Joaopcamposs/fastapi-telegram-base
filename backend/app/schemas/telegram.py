from pydantic import BaseModel, Field


class SendPhotoRequest(BaseModel):
    """Entrada para envio de foto em chat, grupo ou canal."""

    reference: str = Field(min_length=1, max_length=120)
    chat_id: str = Field(min_length=1, examples=["@my_channel"])
    photo_url: str = Field(min_length=1)
    caption: str | None = Field(default=None, max_length=1024)


class EditPhotoRequest(BaseModel):
    """Entrada para edição de foto usando referência salva."""

    photo_url: str = Field(min_length=1)
    caption: str | None = Field(default=None, max_length=1024)


class TelegramMessageResponse(BaseModel):
    """Resposta com os dados mínimos da mensagem persistida."""

    reference: str
    chat_id: str
    message_id: int
    caption: str | None = None
