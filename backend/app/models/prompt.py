# Prompt Model
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.core.database import Base


class Prompt(Base):
    __tablename__ = "prompts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    model_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    prompt_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    tags: Mapped[str] = mapped_column(String(500), default="", nullable=False)  # comma-separated
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_prompts_model_default", "model_name", "is_default"),
    )

    def __repr__(self) -> str:
        return f"<Prompt(id={self.id}, model='{self.model_name}', default={self.is_default})>"