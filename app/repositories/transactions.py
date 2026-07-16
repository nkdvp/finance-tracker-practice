from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import UUID
from app.enums import TransactionType

@dataclass(frozen=True, slots=True)
class TransactionRecord():
    id: UUID
    description: str
    amount: Decimal
    transaction_type: TransactionType
    occurred_on: date
    created_at: datetime
    audit_note: str

class TransactionRepository:
    def create(self, payload) -> TransactionRecord: ...

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

    def create(self, payload) -> TransactionRecord:
        record = TransactionRecord(
            id=UUID(),
            description=payload.description,
            amount=payload.amount,
            transaction_type=payload.transaction_type,
            occurred_on=payload.occurred_on,
            created_at=datetime.now(),
            audit_note="created-via-api",
        )
        self._records[record.id] = record
        return record

    def get_by_id(self, transaction_id: UUID) -> TransactionRecord | None:
        return self._records.get(transaction_id)