from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from django.db.models import QuerySet

T = TypeVar("T")


@dataclass
class Page(Generic[T]):
    results: list[T]
    count: int
    next_cursor: str | None
    previous_cursor: str | None
    has_next: bool
    has_previous: bool


def paginate(
    queryset: QuerySet,
    page: int = 1,
    page_size: int = 24,
) -> dict[str, Any]:
    total = queryset.count()
    offset = (page - 1) * page_size
    results = list(queryset[offset : offset + page_size])
    has_next = (offset + page_size) < total
    has_previous = page > 1

    return {
        "results": results,
        "count": total,
        "page": page,
        "page_size": page_size,
        "has_next": has_next,
        "has_previous": has_previous,
        "total_pages": max(1, -(-total // page_size)),
    }
