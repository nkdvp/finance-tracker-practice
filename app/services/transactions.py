from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import TransactionType
from app.errors import BusinessRuleViolationError, ResourceNotFoundError
from app.models.categories import Category
from app.models.transactions import Transaction
from app.repositories.categories import CategoryRepository
from app.repositories.transactions import TransactionRepository
from app.repositories.users import UserRepository
from app.schemas.transactions import TransactionCreate, TransactionUpdate


class TransactionService:
    """Coordinate transaction rules across user, category, and transaction data."""

    def __init__(
        self,
        session: AsyncSession,
        repository: TransactionRepository,
        user_repository: UserRepository,
        category_repository: CategoryRepository,
    ) -> None:
        self.session = session
        self.repository = repository
        self.user_repository = user_repository
        self.category_repository = category_repository

    async def create(self, payload: TransactionCreate) -> Transaction:
        if await self.user_repository.get_by_id(payload.user_id) is None:
            raise ResourceNotFoundError("User", payload.user_id)

        await self._validate_category(
            category_id=payload.category_id,
            user_id=payload.user_id,
            transaction_type=payload.transaction_type,
        )

        try:
            transaction = await self.repository.create(payload)
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            raise BusinessRuleViolationError(
                "transaction_constraint_violation",
                "The transaction violates a database constraint",
            ) from exc

        await self.session.refresh(transaction)
        return transaction

    async def list(
        self,
        *,
        user_id: UUID | None,
        category_id: UUID | None,
        transaction_type: TransactionType | None,
        offset: int,
        limit: int,
    ) -> tuple[list[Transaction], int]:
        return await self.repository.list(
            user_id=user_id,
            category_id=category_id,
            transaction_type=transaction_type,
            offset=offset,
            limit=limit,
        )

    async def get(self, transaction_id: UUID) -> Transaction:
        transaction = await self.repository.get_by_id(transaction_id)
        if transaction is None:
            raise ResourceNotFoundError("Transaction", transaction_id)
        return transaction

    async def update(
        self,
        transaction_id: UUID,
        payload: TransactionUpdate,
    ) -> Transaction:
        transaction = await self.get(transaction_id)
        category_id = payload.category_id or transaction.category_id
        transaction_type = payload.transaction_type or transaction.transaction_type
        await self._validate_category(
            category_id=category_id,
            user_id=transaction.user_id,
            transaction_type=transaction_type,
        )

        try:
            transaction = await self.repository.update(transaction, payload)
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            raise BusinessRuleViolationError(
                "transaction_constraint_violation",
                "The transaction violates a database constraint",
            ) from exc

        await self.session.refresh(transaction)
        return transaction

    async def delete(self, transaction_id: UUID) -> None:
        transaction = await self.get(transaction_id)
        await self.repository.delete(transaction)
        await self.session.commit()

    async def _validate_category(
        self,
        *,
        category_id: UUID,
        user_id: UUID,
        transaction_type: TransactionType,
    ) -> Category:
        category = await self.category_repository.get_by_id(category_id)
        if category is None:
            raise ResourceNotFoundError("Category", category_id)
        if category.user_id != user_id:
            raise BusinessRuleViolationError(
                "category_ownership_mismatch",
                "The category does not belong to this user",
            )
        if category.transaction_type != transaction_type:
            raise BusinessRuleViolationError(
                "transaction_category_type_mismatch",
                "Transaction type must match category type",
            )
        return category
