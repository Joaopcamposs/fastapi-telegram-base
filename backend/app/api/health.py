from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Retorna o status básico da aplicação."""
    return {"status": "ok"}
