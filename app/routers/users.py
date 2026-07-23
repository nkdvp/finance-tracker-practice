from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.dependencies import UserServiceDep
from app.models.users import User
from app.schemas.users import UserCreate, UserListResponse, UserQuery, UserResponse


router = APIRouter(prefix="/users", tags=["users"])
UserQueryDep = Annotated[UserQuery, Query()]


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, service: UserServiceDep) -> User:
    return await service.create(payload)


@router.get("", response_model=UserListResponse)
async def list_users(filters: UserQueryDep, service: UserServiceDep) -> UserListResponse:
    users, total = await service.list(offset=filters.offset, limit=filters.limit)
    return UserListResponse(
        items=[UserResponse.model_validate(user) for user in users],
        total=total,
        offset=filters.offset,
        limit=filters.limit,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID, service: UserServiceDep) -> User:
    return await service.get(user_id)
