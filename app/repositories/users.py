from typing import Protocol
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User
from app.schemas.users import UserCreate


class UserRepository(Protocol):
    async def create(self, payload: UserCreate) -> User: ...

    async def get_by_id(self, user_id: UUID) -> User | None: ...

    async def list(self, *, offset: int, limit: int) -> tuple[list[User], int]: ...


class SqlAlchemyUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, payload: UserCreate) -> User:
        user = User(**payload.model_dump())
        self.session.add(user)
        # flush sends SQL while leaving commit/rollback to the service use case.
        await self.session.flush()
        return user

    async def get_by_id(self, user_id: UUID) -> User | None:
        return await self.session.get(User, user_id)

    async def list(self, *, offset: int, limit: int) -> tuple[list[User], int]:
        statement = select(User).order_by(User.created_at, User.id).offset(offset).limit(limit)
        result = await self.session.scalars(statement)
        total = await self.session.scalar(select(func.count()).select_from(User))
        return list(result.all()), int(total or 0)
