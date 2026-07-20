from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from uuid import UUID
from app.schemas.transactions import TransactionCreate, TransactionListResponse, TransactionQuery, TransactionResponse
from app.dependencies import TransactionRepositoryDep
from app.repositories.transactions import TransactionRecord



router = APIRouter(prefix="/transactions", tags=["transactions"])

TransactionQueryDep = Annotated[TransactionQuery, Query()]

@router.post(
    "",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(
    payload: TransactionCreate,
    repository: TransactionRepositoryDep,
) -> TransactionRecord:
    return repository.create(payload)

@router.get("", response_model=TransactionListResponse)
def list_transactions(
    filters: TransactionQueryDep,
    repository: TransactionRepositoryDep,
) -> TransactionListResponse:
    records, total = repository.list(
        transaction_type=filters.transaction_type,
        offset=filters.offset,
        limit=filters.limit,
    )
    return TransactionListResponse(
        items=[TransactionResponse.model_validate(record) for record in records], 
        total=total,
        offset=filters.offset,
        limit=filters.limit,
    )

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: UUID,
    repository: TransactionRepositoryDep,
) -> TransactionRecord:
    record = repository.get_by_id(transaction_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    return record