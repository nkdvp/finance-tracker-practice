from __future__ import annotations
from typing import TYPE_CHECKING

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utc_now


if TYPE_CHECKING:
    from app.models.categories import Category
    from app.models.transactions import Transaction


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )

    categories: Mapped[list[Category]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    transactions: Mapped[list[Transaction]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
