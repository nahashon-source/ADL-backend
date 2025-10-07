from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """
    Standard pagination parameters.
    """
    page: int = Field(default=1, ge=1, description="Page number (starts at 1)")
    page_size: int = Field(default=10, ge=1, le=100, description="Items per page (max 100)")

    @property
    def offset(self) -> int:
        """Calculate SQL offset from page number."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Return page_size as limit."""
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response wrapper.
    """
    items: List[T] = Field(description="List of items for current page")
    total: int = Field(description="Total number of items across all pages")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Number of items per page")
    total_pages: int = Field(description="Total number of pages")

    @classmethod
    def create(cls, items: List[T], total: int, page: int, page_size: int):
        """
        Factory method to create paginated response.
        """
        total_pages = (total + page_size - 1) // page_size  # Ceiling division
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
