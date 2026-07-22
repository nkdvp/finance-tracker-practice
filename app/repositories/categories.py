from typing import Protocol
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import TransactionType
from app.models.categories import Category
from app.models.transactions import Transaction
from app.schemas.categories import CategoryCreate, CategoryUpdate


class CategoryRepository(Protocol):
    async def create(self, payload: CategoryCreate) -> Category: ...

    async def get_by_id(self, category_id: UUID) -> Category | None: ...

    async def list(
        self,
        *,
        user_id: UUID | None,
        transaction_type: TransactionType | None,
        offset: int,
        limit: int,
    ) -> tuple[list[Category], int]: ...

    async def update(self, category: Category, payload: CategoryUpdate) -> Category: ...

    async def has_transactions(self, category_id: UUID) -> bool: ...

    async def delete(self, category: Category) -> None: ...


class SqlAlchemyCategoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, payload: CategoryCreate) -> Category:
        category = Category(**payload.model_dump())
        self.session.add(category)
        await self._commit()
        await self.session.refresh(category)
        return category

    async def get_by_id(self, category_id: UUID) -> Category | None:
        return await self.session.get(Category, category_id)

    async def list(
        self,
        *,
        user_id: UUID | None,
        transaction_type: TransactionType | None,
        offset: int,
        limit: int,
    ) -> tuple[list[Category], int]:
        items_statement = select(Category)
        count_statement = select(func.count()).select_from(Category)

        if user_id is not None:
            items_statement = items_statement.where(Category.user_id == user_id)
            count_statement = count_statement.where(Category.user_id == user_id)
        if transaction_type is not None:
            items_statement = items_statement.where(
                Category.transaction_type == transaction_type
            )
            count_statement = count_statement.where(
                Category.transaction_type == transaction_type
            )

        items_statement = (
            items_statement.order_by(Category.name, Category.id).offset(offset).limit(limit)
        )
        result = await self.session.scalars(items_statement)
        total = await self.session.scalar(count_statement)
        # Should not use concurrency here because the two queries are dependent on each other and the session is not thread-safe. Using asyncio.gather would cause a race condition
        # result, total = await asyncio.gather(
        #     self.session.scalars(items_statement),
        #     self.session.scalar(count_statement),
        # )
        return list(result.all()), int(total or 0)

    async def update(self, category: Category, payload: CategoryUpdate) -> Category:
        for field_name, value in payload.model_dump(exclude_unset=True).items():
            setattr(category, field_name, value)

        await self._commit()
        await self.session.refresh(category)
        return category

    async def has_transactions(self, category_id: UUID) -> bool:
        statement = select(Transaction.id).where(Transaction.category_id == category_id).limit(1)
        return await self.session.scalar(statement) is not None

    async def delete(self, category: Category) -> None:
        await self.session.delete(category)
        await self._commit()

    async def _commit(self) -> None:
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise
