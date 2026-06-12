"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import bisect
import dataclasses
import enum
import heapq
import json
import random
import re
import time
from collections import Counter, defaultdict, deque
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    ClassVar,
    Generic,
    Iterator,
    Literal,
    Protocol,
    TypeVar,
    overload,
    runtime_checkable,
)

if TYPE_CHECKING:
    pass  # keep TYPE_CHECKING branch exercised

K = TypeVar("K")
V = TypeVar("V")
T = TypeVar("T")

# ── Enums ─────────────────────────────────────────────────────────────────────

class Status(enum.Enum):
    PENDING   = "pending"
    RUNNING   = "running"
    SUCCESS   = "success"
    FAILED    = "failed"
    CANCELLED = "cancelled"

    def is_terminal(self) -> bool:
        return self in {Status.SUCCESS, Status.FAILED, Status.CANCELLED}


class Priority(enum.IntEnum):
    LOW    = 1
    NORMAL = 5
    HIGH   = 10
    URGENT = 20


class Flag(enum.Flag):
    READ    = enum.auto()
    WRITE   = enum.auto()
    EXECUTE = enum.auto()
    RWX     = READ | WRITE | EXECUTE


# ── Protocols ─────────────────────────────────────────────────────────────────

@runtime_checkable
class Serialisable(Protocol):
    def to_dict(self) -> dict: ...

    @classmethod
    def from_dict(cls, data: dict) -> "Serialisable": ...


@runtime_checkable
class Runnable(Protocol):
    async def run(self) -> str: ...


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Author:
    full_name: str
    twitter_handle: str
    website: str
    avatar_url: str

    @classmethod
    def from_str(
        cls,
        author_string: str,
    ) -> Author:
        regex = r"^([\s\S]+)\s?@\w+\s?(https?:\/\/\S+)$"
        match = re.match(regex, author_string.strip())
        if not match:
            raise ValueError(f"Invalid author string format: '{author_string}'")
        group = match.group(1).split()
        full_name = ' '.join(group[:-1])
        twitter_handle = group[-1]
        website = match.group(2)
        avatar_url = f"{website}/static/images/logo.png"
        return cls(full_name=full_name, twitter_handle=twitter_handle, website=website, avatar_url=avatar_url)


@dataclasses.dataclass(frozen=False)
class Book:
    title: str
    authors: list[Author]
    pages: int
    published_on: str
    publisher: str
    genre: str
    rating: float = 0.0
    reviews_count: int = 0
    price: float = 0.0
    description: str = ""

    def get_author_names(self) -> str:
        return ', '.join(author.full_name for author in self.authors)

    def get_rating_as_percentage(self) -> str:
        return f'{self.rating * 100:.2f}%'

    def get_short_description(self) -> str:
        return f'{self.title} by {self.get_author_names()}'

    def update_rating(self, new_rating: float) -> None:
        self.rating = new_rating

    def update_reviews_count(self, count: int) -> None:
        self.reviews_count = count

    def update_price(self, new_price: float) -> None:
        self.price = new_price

    def add_review(self, review_text: str) -> None:
        self.description += f"\n{review_text}"

    def add_author(self, author: Author) -> None:
        self.authors.append(author)


def main():
    book_1 = Book(
        title="The Great Gatsby",
        authors=[
            Author.from_str("J.D. Salinger (@jdsalinger) https://www.jdsalinger.com"),
            Author.from_str