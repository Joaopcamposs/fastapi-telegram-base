from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_telegram_message_service
from app.schemas.telegram import EditPhotoRequest, SendPhotoRequest, TelegramMessageResponse
from app.services.telegram_message_service import MessageNotFoundError, TelegramMessageService

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post(
    "/messages/photo", response_model=TelegramMessageResponse, status_code=status.HTTP_201_CREATED
)
async def send_photo(
    request: SendPhotoRequest,
    service: TelegramMessageService = Depends(get_telegram_message_service),
) -> TelegramMessageResponse:
    """Envia foto para chat, grupo ou canal e salva o ID da mensagem."""
    return await service.send_photo(request)


@router.patch("/messages/{reference}/photo", response_model=TelegramMessageResponse)
async def edit_photo(
    reference: str,
    request: EditPhotoRequest,
    service: TelegramMessageService = Depends(get_telegram_message_service),
) -> TelegramMessageResponse:
    """Edita foto enviada anteriormente usando a referência salva."""
    try:
        return await service.edit_photo(reference, request)
    except MessageNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/webhook/{secret}")
async def telegram_webhook(secret: str, update: dict[str, Any]) -> dict[str, bool]:
    """Recebe updates do Telegram dentro do app FastAPI.

    O segredo fica na URL configurada no setWebhook. Esta base apenas confirma o update;
    adicione handlers de comandos aqui quando necessário.
    """
    _ = secret, update
    return {"ok": True}
