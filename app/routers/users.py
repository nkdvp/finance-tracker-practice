from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status
from sqlalchemy.exc import IntegrityError

from app.dependencies import UserRepositoryDep
from app.errors import DuplicateResourceError, ResourceNotFoundError
from app.models.users import User
from app.schemas.users import UserCreate, UserListResponse, UserQuery, UserResponse


router = APIRouter(prefix="/users", tags=["users"])
UserQueryDep = Annotated[UserQuery, Query()]


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, repository: UserRepositoryDep) -> User:
    try:
        return await repository.create(payload)
    except IntegrityError as exc:
        raise DuplicateResourceError(
            "User",
            "A user with this email already exists",
        ) from exc


@router.get("", response_model=UserListResponse)
async def list_users(filters: UserQueryDep, repository: UserRepositoryDep) -> UserListResponse:
    users, total = await repository.list(offset=filters.offset, limit=filters.limit)
    return UserListResponse(
        items=[UserResponse.model_validate(user) for user in users],
        total=total,
        offset=filters.offset,
        limit=filters.limit,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID, repository: UserRepositoryDep) -> User:
    user = await repository.get_by_id(user_id)
    if user is None:
        raise ResourceNotFoundError("User", user_id)
    return user
