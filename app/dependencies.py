from fastapi.params import Depends
from typing_extensions import Annotated

from app.repositories.transactions import (
    InMemoryTransactionRepository,
    TransactionRepository,
)

_repository: TransactionRepository = InMemoryTransactionRepository()


def get_transaction_repository() -> TransactionRepository:
    """Provide the current transaction storage implementation."""
    return _repository


TransactionRepositoryDep = Annotated[
    TransactionRepository,
    Depends(get_transaction_repository),
]