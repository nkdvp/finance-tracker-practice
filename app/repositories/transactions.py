from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Protocol
from uuid import UUID, uuid4

from app.enums import TransactionType
from app.schemas.transactions import TransactionCreate


@dataclass(frozen=True, slots=True)
class TransactionRecord:
    id: UUID
    description: str
    amount: Decimal
    transaction_type: TransactionType
    occurred_on: date
    created_at: datetime
    audit_note: str


class TransactionRepository(Protocol):
    """Storage contract shared by in-memory and future database repositories.

    A Protocol uses structural typing: an implementation only needs matching
    methods; it does not need to inherit from TransactionRepository.
    """

    def create(self, payload: TransactionCreate) -> TransactionRecord: ...

    def get_by_id(self, transaction_id: UUID) -> TransactionRecord | None: ...

    def list(
        self,
        *,
        transaction_type: TransactionType | None,
        offset: int,
        limit: int,
    ) -> tuple[list[TransactionRecord], int]: ...


class InMemoryTransactionRepository:
    def __init__(self) -> None:
        self._records: dict[UUID, TransactionRecord] = {}

    def create(self, payload: TransactionCreate) -> TransactionRecord:
        record = TransactionRecord(
            id=uuid4(),
            description=payload.description,
            amount=payload.amount,
            transaction_type=payload.transaction_type,
            occurred_on=payload.occurred_on,
            # Include the UTC offset so API clients can interpret this timestamp reliably.
            created_at=datetime.now(timezone.utc),
            audit_note="created-via-api",
        )
        self._records[record.id] = record
        return record

    def get_by_id(self, transaction_id: UUID) -> TransactionRecord | None:
        return self._records.get(transaction_id)

    def list(
        self,
        *,
        transaction_type: TransactionType | None,
        offset: int,
        limit: int,
    ) -> tuple[list[TransactionRecord], int]:
        records = list(self._records.values())
        if transaction_type is not None:
            records = [r for r in records if r.transaction_type == transaction_type]
        total = len(records)
        return records[offset : offset + limit], total
