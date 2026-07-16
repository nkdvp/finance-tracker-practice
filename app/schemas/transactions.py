from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from app.enums import TransactionType


class TransactionBase(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        str_strip_whitespace=True,
    )

    description: str = Field(min_length=1, max_length=200)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    transaction_type: TransactionType = Field(alias="type")
    occurred_on: date
# description       str, từ 1 đến 200 ký tự
# amount            Decimal, lớn hơn 0, tối đa 2 số thập phân
# type              income hoặc expense
# occurred_on       date

class TransactionCreate(TransactionBase):
    """Fields a client is allowed to send when creating a transaction."""

class TransactionResponse(TransactionBase):
    """Fields the API guarantees to return to a client."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime

class TransactionQuery(BaseModel):
    """Validated query-string filters for the list endpoint."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    transaction_type: TransactionType | None = Field(default=None, alias="type")
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)

class TransactionListResponse(BaseModel):
    items: list[TransactionResponse]
    total: int = Field(ge=0)
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)