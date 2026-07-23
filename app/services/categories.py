from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import TransactionType
from app.errors import DuplicateResourceError, ResourceInUseError, ResourceNotFoundError
from app.models.categories import Category
from app.repositories.categories import CategoryRepository
from app.repositories.users import UserRepository
from app.schemas.categories import CategoryCreate, CategoryUpdate


class CategoryService:
    """Apply category business rules before using persistence operations."""

    def __init__(
        self,
        session: AsyncSession,
        repository: CategoryRepository,
        user_repository: UserRepository,
    ) -> None:
        self.session = session
        self.repository = repository
        self.user_repository = user_repository

    async def create(self, payload: CategoryCreate) -> Category:
        if await self.user_repository.get_by_id(payload.user_id) is None:
            raise ResourceNotFoundError("User", payload.user_id)

        try:
            category = await self.repository.create(payload)
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            raise DuplicateResourceError(
                "Category",
                "This user already has a category with the same name and type",
            ) from exc

        await self.session.refresh(category)
        return category

    async def list(
        self,
        *,
        user_id: UUID | None,
        transaction_type: TransactionType | None,
        offset: int,
        limit: int,
    ) -> tuple[list[Category], int]:
        return await self.repository.list(
            user_id=user_id,
            transaction_type=transaction_type,
            offset=offset,
            limit=limit,
        )

    async def get(self, category_id: UUID) -> Category:
        category = await self.repository.get_by_id(category_id)
        if category is None:
            raise ResourceNotFoundError("Category", category_id)
        return category

    async def update(self, category_id: UUID, payload: CategoryUpdate) -> Category:
        category = await self.get(category_id)
        type_is_changing = (
            payload.transaction_type is not None
            and payload.transaction_type != category.transaction_type
        )
        if type_is_changing and await self.repository.has_transactions(category.id):
            raise ResourceInUseError(
                "Category",
                category.id,
                "A category with transactions cannot change its type",
            )

        try:
            category = await self.repository.update(category, payload)
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            raise DuplicateResourceError(
                "Category",
                "This user already has a category with the same name and type",
            ) from exc

        await self.session.refresh(category)
        return category

    async def delete(self, category_id: UUID) -> None:
        category = await self.get(category_id)
        if await self.repository.has_transactions(category.id):
            raise ResourceInUseError(
                "Category",
                category.id,
                "Delete this category's transactions before deleting the category",
            )

        try:
            await self.repository.delete(category)
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            raise ResourceInUseError(
                "Category",
                category.id,
                "Delete this category's transactions before deleting the category",
            ) from exc
