from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# EmailStr performs syntax/normalization validation through email-validator;
# Annotated adds the database-compatible maximum length to that reusable type.
Email = Annotated[EmailStr, Field(max_length=320)]


class UserBase(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    email: Email
    display_name: str = Field(min_length=1, max_length=100)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        """Apply the application's case-insensitive uniqueness policy."""
        return str(value).lower()


class UserCreate(UserBase):
    """Fields accepted when creating a user."""


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime


class UserQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")

    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class UserListResponse(BaseModel):
    items: list[UserResponse]
    total: int = Field(ge=0)
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
