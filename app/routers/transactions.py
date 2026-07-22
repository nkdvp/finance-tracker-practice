from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError

from app.dependencies import (
    CategoryRepositoryDep,
    TransactionRepositoryDep,
    UserRepositoryDep,
)
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    category = await category_repository.get_by_id(payload.category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    if category.user_id != payload.user_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The category does not belong to this user",
        )
    if category.transaction_type != payload.transaction_type:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Transaction type must match category type",
        )

    try:
        return await repository.create(payload)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The transaction violates a database constraint",
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    category_id = payload.category_id or transaction.category_id
    transaction_type = payload.transaction_type or transaction.transaction_type
    category = await category_repository.get_by_id(category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    if category.user_id != transaction.user_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The category does not belong to this transaction's user",
        )
    if category.transaction_type != transaction_type:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Transaction type must match category type",
        )

    try:
        return await repository.update(transaction, payload)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The transaction violates a database constraint",
        ) from exc


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: UUID,
    repository: TransactionRepositoryDep,
) -> None:
    transaction = await repository.get_by_id(transaction_id)
    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    await repository.delete(transaction)
