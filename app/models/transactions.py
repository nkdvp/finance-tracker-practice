from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums import TransactionType
from app.models.base import Base, utc_now

if TYPE_CHECKING:
    from app.models.categories import Category
    from app.models.users import User


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    category_id: Mapped[UUID] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"),
        index=True,
    )
    description: Mapped[str] = mapped_column(String(200))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    transaction_type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType, native_enum=False, length=20),
    )
    occurred_on: Mapped[date] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )

    user: Mapped[User] = relationship(back_populates="transactions")
    category: Mapped[Category] = relationship(back_populates="transactions")
