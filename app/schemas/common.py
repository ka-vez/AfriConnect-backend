"""
Common schemas used across endpoints.
"""

from pydantic import BaseModel
from typing import Generic, TypeVar, List


T = TypeVar('T')


class ErrorResponse(BaseModel):
    """
    Standard error response format.
    """
    detail: str
    error_code: str | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response wrapper.
    """
    total: int
    page: int
    page_size: int
    items: List[T]
