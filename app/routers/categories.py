from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.dependencies import CategoryServiceDep
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
async def create_category(payload: CategoryCreate, service: CategoryServiceDep) -> Category:
    return await service.create(payload)


@router.get("", response_model=CategoryListResponse)
async def list_categories(
    filters: CategoryQueryDep,
    service: CategoryServiceDep,
) -> CategoryListResponse:
    categories, total = await service.list(
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
async def get_category(category_id: UUID, service: CategoryServiceDep) -> Category:
    return await service.get(category_id)


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    payload: CategoryUpdate,
    service: CategoryServiceDep,
) -> Category:
    return await service.update(category_id, payload)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: UUID, service: CategoryServiceDep) -> None:
    await service.delete(category_id)
