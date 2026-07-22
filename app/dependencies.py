from typing import Annotated

from fastapi import Depends

from app.database import SessionDep
from app.repositories.categories import CategoryRepository, SqlAlchemyCategoryRepository
from app.repositories.transactions import (
    SqlAlchemyTransactionRepository,
    TransactionRepository,
)
from app.repositories.users import SqlAlchemyUserRepository, UserRepository


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
