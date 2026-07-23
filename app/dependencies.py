from typing import Annotated

from fastapi import Depends

from app.database import SessionDep
from app.repositories.categories import CategoryRepository, SqlAlchemyCategoryRepository
from app.repositories.transactions import (
    SqlAlchemyTransactionRepository,
    TransactionRepository,
)
from app.repositories.users import SqlAlchemyUserRepository, UserRepository
from app.services.categories import CategoryService
from app.services.transactions import TransactionService
from app.services.users import UserService


def get_user_repository(session: SessionDep) -> UserRepository:
    return SqlAlchemyUserRepository(session)


def get_category_repository(session: SessionDep) -> CategoryRepository:
    return SqlAlchemyCategoryRepository(session)


def get_transaction_repository(session: SessionDep) -> TransactionRepository:
    return SqlAlchemyTransactionRepository(session)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
CategoryRepositoryDep = Annotated[CategoryRepository, Depends(get_category_repository)]
TransactionRepositoryDep = Annotated[
    TransactionRepository,
    Depends(get_transaction_repository),
]


def get_user_service(session: SessionDep, repository: UserRepositoryDep) -> UserService:
    return UserService(session, repository)


def get_category_service(
    session: SessionDep,
    repository: CategoryRepositoryDep,
    user_repository: UserRepositoryDep,
) -> CategoryService:
    return CategoryService(session, repository, user_repository)


def get_transaction_service(
    session: SessionDep,
    repository: TransactionRepositoryDep,
    user_repository: UserRepositoryDep,
    category_repository: CategoryRepositoryDep,
) -> TransactionService:
    return TransactionService(
        session,
        repository,
        user_repository,
        category_repository,
    )


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]
TransactionServiceDep = Annotated[TransactionService, Depends(get_transaction_service)]
