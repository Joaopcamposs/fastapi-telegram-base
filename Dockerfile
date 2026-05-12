FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml README.md ./
RUN uv sync --no-dev

COPY backend ./src

EXPOSE 8000
CMD ["uv", "run", "fastapi", "run", "src/app/main.py", "--host", "0.0.0.0", "--port", "8000"]
