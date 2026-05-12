from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.models.telegram_message import TelegramMessage
from app.repositories.telegram_message_repository import TelegramMessageRepository
from app.schemas.telegram import EditPhotoRequest, SendPhotoRequest
from app.services.telegram_message_service import MessageNotFoundError, TelegramMessageService


class FakeTelegramClient:
    """Cliente fake para testar o serviço sem chamar a rede."""

    def __init__(self) -> None:
        self.edits: list[dict[str, object]] = []

    async def send_photo(
        self, *, chat_id: str, photo_url: str, caption: str | None
    ) -> dict[str, object]:
        return {"ok": True, "result": {"message_id": 42, "chat": {"id": chat_id}}}

    async def edit_photo(
        self,
        *,
        chat_id: str,
        message_id: int,
        photo_url: str,
        caption: str | None,
    ) -> dict[str, object]:
        self.edits.append(
            {
                "chat_id": chat_id,
                "message_id": message_id,
                "photo_url": photo_url,
                "caption": caption,
            }
        )
        return {"ok": True, "result": True}


@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as session:
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_repository_saves_and_updates_message(session: AsyncSession) -> None:
    repository = TelegramMessageRepository(session)

    created = await repository.save_sent_message(
        reference="daily-post",
        chat_id="@channel",
        message_id=1,
        caption="first",
    )
    updated = await repository.save_sent_message(
        reference="daily-post",
        chat_id="@channel",
        message_id=2,
        caption="second",
    )

    assert created.id == updated.id
    assert updated.message_id == 2
    assert updated.caption == "second"


@pytest.mark.asyncio
async def test_service_send_photo_persists_message_id(session: AsyncSession) -> None:
    service = TelegramMessageService(
        client=FakeTelegramClient(),
        repository=TelegramMessageRepository(session),
    )

    response = await service.send_photo(
        SendPhotoRequest(
            reference="launch",
            chat_id="@news",
            photo_url="https://example.com/image.png",
            caption="Launch",
        )
    )

    assert response.reference == "launch"
    assert response.chat_id == "@news"
    assert response.message_id == 42


@pytest.mark.asyncio
async def test_service_edit_photo_uses_saved_message_id(session: AsyncSession) -> None:
    client = FakeTelegramClient()
    repository = TelegramMessageRepository(session)
    await repository.save_sent_message(reference="launch", chat_id="@news", message_id=42)

    service = TelegramMessageService(client=client, repository=repository)
    response = await service.edit_photo(
        "launch",
        EditPhotoRequest(photo_url="https://example.com/new.png", caption="Updated"),
    )

    assert response.caption == "Updated"
    assert client.edits == [
        {
            "chat_id": "@news",
            "message_id": 42,
            "photo_url": "https://example.com/new.png",
            "caption": "Updated",
        }
    ]


@pytest.mark.asyncio
async def test_service_edit_photo_raises_for_missing_reference(session: AsyncSession) -> None:
    service = TelegramMessageService(
        client=FakeTelegramClient(),
        repository=TelegramMessageRepository(session),
    )

    with pytest.raises(MessageNotFoundError):
        await service.edit_photo(
            "missing", EditPhotoRequest(photo_url="https://example.com/new.png")
        )


def test_model_table_name() -> None:
    assert TelegramMessage.__tablename__ == "telegram_messages"
