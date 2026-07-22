from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status
from sqlalchemy.exc import IntegrityError

from app.dependencies import (
    CategoryRepositoryDep,
    TransactionRepositoryDep,
    UserRepositoryDep,
)
from app.errors import BusinessRuleViolationError, ResourceNotFoundError
from app.models.transactions import Transaction
from app.schemas.transactions import (
    TransactionCreate,
    TransactionListResponse,
    TransactionQuery,
    TransactionResponse,
    TransactionUpdate,
)


router = APIRouter(prefix="/transactions", tags=["transactions"])
TransactionQueryDep = Annotated[TransactionQuery, Query()]


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    payload: TransactionCreate,
    repository: TransactionRepositoryDep,
    user_repository: UserRepositoryDep,
    category_repository: CategoryRepositoryDep,
) -> Transaction:
    if await user_repository.get_by_id(payload.user_id) is None:
        raise ResourceNotFoundError("User", payload.user_id)

    category = await category_repository.get_by_id(payload.category_id)
    if category is None:
        raise ResourceNotFoundError("Category", payload.category_id)
    if category.user_id != payload.user_id:
        raise BusinessRuleViolationError(
            "category_ownership_mismatch",
            "The category does not belong to this user",
        )
    if category.transaction_type != payload.transaction_type:
        raise BusinessRuleViolationError(
            "transaction_category_type_mismatch",
            "Transaction type must match category type",
        )

    try:
        return await repository.create(payload)
    except IntegrityError as exc:
        raise BusinessRuleViolationError(
            "transaction_constraint_violation",
            "The transaction violates a database constraint",
        ) from exc


@router.get("", response_model=TransactionListResponse)
async def list_transactions(
    filters: TransactionQueryDep,
    repository: TransactionRepositoryDep,
) -> TransactionListResponse:
    transactions, total = await repository.list(
        user_id=filters.user_id,
        category_id=filters.category_id,
        transaction_type=filters.transaction_type,
        offset=filters.offset,
        limit=filters.limit,
    )
    return TransactionListResponse(
        items=[TransactionResponse.model_validate(transaction) for transaction in transactions],
        total=total,
        offset=filters.offset,
        limit=filters.limit,
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: UUID,
    repository: TransactionRepositoryDep,
) -> Transaction:
    transaction = await repository.get_by_id(transaction_id)
    if transaction is None:
        raise ResourceNotFoundError("Transaction", transaction_id)
    return transaction


@router.patch("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: UUID,
    payload: TransactionUpdate,
    repository: TransactionRepositoryDep,
    category_repository: CategoryRepositoryDep,
) -> Transaction:
    transaction = await repository.get_by_id(transaction_id)
    if transaction is None:
        raise ResourceNotFoundError("Transaction", transaction_id)

    category_id = payload.category_id or transaction.category_id
    transaction_type = payload.transaction_type or transaction.transaction_type
    category = await category_repository.get_by_id(category_id)
    if category is None:
        raise ResourceNotFoundError("Category", category_id)
    if category.user_id != transaction.user_id:
        raise BusinessRuleViolationError(
            "category_ownership_mismatch",
            "The category does not belong to this transaction's user",
        )
    if category.transaction_type != transaction_type:
        raise BusinessRuleViolationError(
            "transaction_category_type_mismatch",
            "Transaction type must match category type",
        )

    try:
        return await repository.update(transaction, payload)
    except IntegrityError as exc:
        raise BusinessRuleViolationError(
            "transaction_constraint_violation",
            "The transaction violates a database constraint",
        ) from exc


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: UUID,
    repository: TransactionRepositoryDep,
) -> None:
    transaction = await repository.get_by_id(transaction_id)
    if transaction is None:
        raise ResourceNotFoundError("Transaction", transaction_id)
    await repository.delete(transaction)
