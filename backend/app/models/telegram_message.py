from sqlalchemy import BigInteger, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import EntityBase


class TelegramMessage(EntityBase):
    """Mensagem enviada pelo bot e salva para edição futura."""

    __tablename__ = "telegram_messages"
    __table_args__ = (UniqueConstraint("reference", name="uq_telegram_messages_reference"),)

    reference: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    chat_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    media_type: Mapped[str] = mapped_column(String(30), nullable=False, default="photo")
    caption: Mapped[str | None] = mapped_column(String(1024), nullable=True)
