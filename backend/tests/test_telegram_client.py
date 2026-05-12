import httpx
import pytest

from app.services.telegram_client import TelegramClient, TelegramClientError


@pytest.mark.asyncio
async def test_send_photo_posts_expected_payload() -> None:
    captured: dict[str, object] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["json"] = request.read().decode()
        return httpx.Response(
            200,
            json={"ok": True, "result": {"message_id": 10, "chat": {"id": -100}}},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = TelegramClient(
            bot_token="token",
            api_base_url="https://api.telegram.org",
            http_client=http_client,
        )
        response = await client.send_photo(
            chat_id="@channel",
            photo_url="https://example.com/a.png",
            caption="hello",
        )

    assert response["ok"] is True
    assert captured["url"] == "https://api.telegram.org/bottoken/sendPhoto"
    assert '"chat_id":"@channel"' in str(captured["json"])


@pytest.mark.asyncio
async def test_edit_photo_posts_input_media() -> None:
    captured: dict[str, object] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["json"] = request.read().decode()
        return httpx.Response(200, json={"ok": True, "result": True})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = TelegramClient(
            bot_token="token", api_base_url="https://api.telegram.org", http_client=http_client
        )
        await client.edit_photo(
            chat_id="-100",
            message_id=99,
            photo_url="https://example.com/b.png",
            caption="updated",
        )

    body = str(captured["json"])
    assert "editMessageMedia" not in body
    assert '"message_id":99' in body
    assert '"type":"photo"' in body
    assert '"caption":"updated"' in body


@pytest.mark.asyncio
async def test_client_raises_when_telegram_returns_error() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"ok": False, "description": "bad request"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = TelegramClient(
            bot_token="token", api_base_url="https://api.telegram.org", http_client=http_client
        )
        with pytest.raises(TelegramClientError, match="bad request"):
            await client.send_photo(chat_id="@channel", photo_url="x", caption=None)


@pytest.mark.asyncio
async def test_client_raises_without_token() -> None:
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda request: httpx.Response(200))
    ) as http_client:
        client = TelegramClient(
            bot_token="", api_base_url="https://api.telegram.org", http_client=http_client
        )
        with pytest.raises(TelegramClientError, match="not configured"):
            await client.send_photo(chat_id="@channel", photo_url="x", caption=None)
