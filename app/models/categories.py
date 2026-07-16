from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums import TransactionType
from app.models.base import Base, utc_now

if TYPE_CHECKING:
    from app.models.transactions import Transaction
    from app.models.users import User


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "name",
            "transaction_type",
            name="uq_categories_user_name_type",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100))
    transaction_type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType, native_enum=False, length=20),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )

    user: Mapped[User] = relationship(back_populates="categories")
    transactions: Mapped[list[Transaction]] = relationship(
        back_populates="category",
    )
