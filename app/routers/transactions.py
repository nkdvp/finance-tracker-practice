from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.dependencies import TransactionServiceDep
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
    service: TransactionServiceDep,
) -> Transaction:
    return await service.create(payload)


@router.get("", response_model=TransactionListResponse)
async def list_transactions(
    filters: TransactionQueryDep,
    service: TransactionServiceDep,
) -> TransactionListResponse:
    transactions, total = await service.list(
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
async def get_transaction(transaction_id: UUID, service: TransactionServiceDep) -> Transaction:
    return await service.get(transaction_id)


@router.patch("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: UUID,
    payload: TransactionUpdate,
    service: TransactionServiceDep,
) -> Transaction:
    return await service.update(transaction_id, payload)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(transaction_id: UUID, service: TransactionServiceDep) -> None:
    await service.delete(transaction_id)
