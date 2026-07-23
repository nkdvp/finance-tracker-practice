from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.errors import DuplicateResourceError, ResourceNotFoundError
from app.models.users import User
from app.repositories.users import UserRepository
from app.schemas.users import UserCreate


class UserService:
    """Coordinate user use cases and their database transaction boundary."""

    def __init__(self, session: AsyncSession, repository: UserRepository) -> None:
        self.session = session
        self.repository = repository

    async def create(self, payload: UserCreate) -> User:
        try:
            user = await self.repository.create(payload)
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            raise DuplicateResourceError(
                "User",
                "A user with this email already exists",
            ) from exc

        await self.session.refresh(user)
        return user

    async def list(self, *, offset: int, limit: int) -> tuple[list[User], int]:
        return await self.repository.list(offset=offset, limit=limit)

    async def get(self, user_id: UUID) -> User:
        user = await self.repository.get_by_id(user_id)
        if user is None:
            raise ResourceNotFoundError("User", user_id)
        return user
