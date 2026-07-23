from typing import Protocol
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import TransactionType
from app.models.transactions import Transaction
from app.schemas.transactions import TransactionCreate, TransactionUpdate


class TransactionRepository(Protocol):
    """Persistence operations required by the transaction router."""

    async def create(self, payload: TransactionCreate) -> Transaction: ...

    async def get_by_id(self, transaction_id: UUID) -> Transaction | None: ...

    async def list(
        self,
        *,
        user_id: UUID | None,
        category_id: UUID | None,
        transaction_type: TransactionType | None,
        offset: int,
        limit: int,
    ) -> tuple[list[Transaction], int]: ...

    async def update(
        self,
        transaction: Transaction,
        payload: TransactionUpdate,
    ) -> Transaction: ...

    async def delete(self, transaction: Transaction) -> None: ...


class SqlAlchemyTransactionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, payload: TransactionCreate) -> Transaction:
        transaction = Transaction(**payload.model_dump())
        self.session.add(transaction)
        await self.session.flush()
        return transaction

    async def get_by_id(self, transaction_id: UUID) -> Transaction | None:
        return await self.session.get(Transaction, transaction_id)

    async def list(
        self,
        *,
        user_id: UUID | None,
        category_id: UUID | None,
        transaction_type: TransactionType | None,
        offset: int,
        limit: int,
    ) -> tuple[list[Transaction], int]:
        items_statement = select(Transaction)
        count_statement = select(func.count()).select_from(Transaction)

        if user_id is not None:
            items_statement = items_statement.where(Transaction.user_id == user_id)
            count_statement = count_statement.where(Transaction.user_id == user_id)
        if category_id is not None:
            items_statement = items_statement.where(Transaction.category_id == category_id)
            count_statement = count_statement.where(Transaction.category_id == category_id)
        if transaction_type is not None:
            items_statement = items_statement.where(
                Transaction.transaction_type == transaction_type
            )
            count_statement = count_statement.where(
                Transaction.transaction_type == transaction_type
            )

        items_statement = (
            items_statement.order_by(Transaction.occurred_on.desc(), Transaction.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.scalars(items_statement)
        total = await self.session.scalar(count_statement)
        return list(result.all()), int(total or 0)

    async def update(
        self,
        transaction: Transaction,
        payload: TransactionUpdate,
    ) -> Transaction:
        for field_name, value in payload.model_dump(exclude_unset=True).items():
            setattr(transaction, field_name, value)

        await self.session.flush()
        return transaction

    async def delete(self, transaction: Transaction) -> None:
        await self.session.delete(transaction)
        await self.session.flush()
