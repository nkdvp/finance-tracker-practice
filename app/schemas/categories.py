from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.enums import TransactionType


class CategoryBase(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        str_strip_whitespace=True,
    )

    name: str = Field(min_length=1, max_length=100)
    transaction_type: TransactionType = Field(alias="type")


class CategoryCreate(CategoryBase):
    user_id: UUID


class CategoryUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True, str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1, max_length=100)
    transaction_type: TransactionType | None = Field(default=None, alias="type")

    @model_validator(mode="after")
    def validate_update(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        if any(getattr(self, field_name) is None for field_name in self.model_fields_set):
            raise ValueError("Update fields cannot be null")
        return self


class CategoryResponse(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    created_at: datetime


class CategoryQuery(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    user_id: UUID | None = None
    transaction_type: TransactionType | None = Field(default=None, alias="type")
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class CategoryListResponse(BaseModel):
    items: list[CategoryResponse]
    total: int = Field(ge=0)
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
