# FastAPI Telegram Base

Base project for a Python FastAPI application with an internal Telegram webhook, PostgreSQL, SQLAlchemy 2.0 async, Docker, Docker Compose, uv, Ruff, ty and unit tests with 80%+ coverage.

The code is intentionally small and readable. Identifiers and code are in English, while docstrings are in Portuguese.

## Features

- FastAPI app factory with `lifespan`.
- Telegram webhook mounted inside the FastAPI app.
- Send photos to chats, groups or channels.
- Edit previously sent photo messages.
- Store `chat_id` and `message_id` in PostgreSQL so messages can be edited later.
- Async SQLAlchemy 2.0 base entity with UUID, `created_at` and `updated_at`.
- PostgreSQL via Docker Compose.
- `uv` for dependency management.
- `ruff` for linting and formatting.
- `ty` for type checking.
- `pytest` and `coverage` with `fail_under = 80`.

## Requirements

- Docker and Docker Compose.
- uv installed locally if you want to run outside Docker.
- A Telegram bot token from BotFather.
- The bot must be an admin in the channel if it will send or edit channel messages.

## Quick start

```bash
cp .env.example .env
make up
```

Create the tables in another terminal:

```bash
make migrate
```

Check the app:

```bash
curl http://localhost:8000/health
```

## Local development without Docker

```bash
cp .env.example .env
uv sync --all-groups
make dev
```

Point `DATABASE_URL` in `.env` to a reachable PostgreSQL instance.

## Telegram webhook

The webhook endpoint is:

```text
POST /telegram/webhook/{TELEGRAM_WEBHOOK_SECRET}
```

For local testing, expose your app with a tunnel and register the webhook:

```bash
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook" \
  -d "url=https://your-public-url.example.com/telegram/webhook/$TELEGRAM_WEBHOOK_SECRET"
```

This base only acknowledges updates. Add command handlers inside `src/app/api/telegram.py` when you need business-specific behavior.

## Send an image to a channel

```bash
curl -X POST http://localhost:8000/telegram/messages/photo \
  -H 'content-type: application/json' \
  -d '{
    "reference": "daily-image",
    "chat_id": "@your_channel",
    "photo_url": "https://example.com/image.png",
    "caption": "First caption"
  }'
```

The response includes the saved `message_id`. The database also stores the same value under `reference`.

## Edit the saved image later

```bash
curl -X PATCH http://localhost:8000/telegram/messages/daily-image/photo \
  -H 'content-type: application/json' \
  -d '{
    "photo_url": "https://example.com/updated-image.png",
    "caption": "Updated caption"
  }'
```

## Make commands

```bash
make install    # uv sync --all-groups
make dev        # run FastAPI locally
make lint       # ruff check
make format     # ruff format + safe fixes
make type       # ty check
make test       # pytest
make coverage   # coverage run/report with 80% gate
make up         # docker compose up --build
make down       # docker compose down -v
make logs       # app logs
make migrate    # create tables for local/dev usage
```

## Project layout

```text
src/app/
  api/          FastAPI routes and dependencies
  core/         settings
  db/           async engine, session and base entity
  models/       SQLAlchemy models
  repositories/ database access
  schemas/      Pydantic request/response models
  services/     Telegram client and business service
tests/          unit tests
```

## Notes

- There is no authentication by design.
- The bot can send and edit channel messages when the bot has permission in the target channel.
- For production, replace `init_db` with Alembic migrations and add request authentication for internal endpoints.
