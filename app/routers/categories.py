from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status
from sqlalchemy.exc import IntegrityError

from app.dependencies import CategoryRepositoryDep, UserRepositoryDep
from app.errors import DuplicateResourceError, ResourceInUseError, ResourceNotFoundError
from app.models.categories import Category
from app.schemas.categories import (
    CategoryCreate,
    CategoryListResponse,
    CategoryQuery,
    CategoryResponse,
    CategoryUpdate,
)


router = APIRouter(prefix="/categories", tags=["categories"])
CategoryQueryDep = Annotated[CategoryQuery, Query()]


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CategoryCreate,
    repository: CategoryRepositoryDep,
    user_repository: UserRepositoryDep,
) -> Category:
    if await user_repository.get_by_id(payload.user_id) is None:
        raise ResourceNotFoundError("User", payload.user_id)

    try:
        return await repository.create(payload)
    except IntegrityError as exc:
        raise DuplicateResourceError(
            "Category",
            "This user already has a category with the same name and type",
        ) from exc


@router.get("", response_model=CategoryListResponse)
async def list_categories(
    filters: CategoryQueryDep,
    repository: CategoryRepositoryDep,
) -> CategoryListResponse:
    categories, total = await repository.list(
        user_id=filters.user_id,
        transaction_type=filters.transaction_type,
        offset=filters.offset,
        limit=filters.limit,
    )
    return CategoryListResponse(
        items=[CategoryResponse.model_validate(category) for category in categories],
        total=total,
        offset=filters.offset,
        limit=filters.limit,
    )


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: UUID, repository: CategoryRepositoryDep) -> Category:
    category = await repository.get_by_id(category_id)
    if category is None:
        raise ResourceNotFoundError("Category", category_id)
    return category


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    payload: CategoryUpdate,
    repository: CategoryRepositoryDep,
) -> Category:
    category = await repository.get_by_id(category_id)
    if category is None:
        raise ResourceNotFoundError("Category", category_id)

    type_is_changing = (
        payload.transaction_type is not None
        and payload.transaction_type != category.transaction_type
    )
    if type_is_changing and await repository.has_transactions(category.id):
        raise ResourceInUseError(
            "Category",
            category.id,
            "A category with transactions cannot change its type",
        )

    try:
        return await repository.update(category, payload)
    except IntegrityError as exc:
        raise DuplicateResourceError(
            "Category",
            "This user already has a category with the same name and type",
        ) from exc


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: UUID, repository: CategoryRepositoryDep) -> None:
    category = await repository.get_by_id(category_id)
    if category is None:
        raise ResourceNotFoundError("Category", category_id)
    if await repository.has_transactions(category.id):
        raise ResourceInUseError(
            "Category",
            category.id,
            "Delete this category's transactions before deleting the category",
        )

    await repository.delete(category)
