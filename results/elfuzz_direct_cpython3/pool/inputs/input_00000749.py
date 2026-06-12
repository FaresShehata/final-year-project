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
    READY   = "ready"
    RUNNING = "running"

@dataclasses.dataclass(frozen=True)
class Document:
    title: str
    author: str
    content: str

@runtime_checkable
class Iterable(Protocol[T]):
    def __iter__(self) -> Iterator[T]: ...

# ── Dataclasses ───────────────────────────────────────────────────────────────

def to_json(obj):
    return {
        "__typename": type(obj).__name__,
        **{k: to_json(v) for k, v in obj.__dict__.items()}
    }

async def _save_to_file(filename:str, contents):
    with open(filename, 'w') as f:
        await f.write(contents)

async def save_to_file(filename:str, contents):
    return await asyncio.get_running_loop().run_in_executor(None, _save_to_file, filename, contents)

async def save_documents(documents:list[Document], filename='documents.json'):
    contents = '\n'.join(json.dumps(to_json(document)) + '\n' for document in documents)
    return await save_to_file(filename, contents)


# ── Async/Await ──────────────────────────────────────────────────────────────

async def get_random_document():
    # a dict containing some dummy data
    docs = {
        1: {"title":"foo", "author":"bar", "content":"Lorem ipsum dolor sit amet"},
        2: {"title":"qux", "author":"baz", "content":"Consectetur adipiscing elit"},
        3: {"title":"flarb", "author":"fizz", "content":"Sed do eiusmod tempor incididunt"}
    }
    keys = list(docs.keys())
    key = random.choice(keys)
    # extract the corresponding value from `docs`
    doc = docs[key]
    return doc

async def get_all_docs():
    return [doc async for doc in get_random_document()]

async def main():
    print('get_random_document()')
    doc = await get_random_document()
    print(f"Title: {doc['title']}")
    print(f"Author: {doc['author']}")
    print(f"Content: {doc['content']}")

    print('\nget_all_docs()')
    docs = await get_all_docs()
    print(len(docs))
    for i, doc in enumerate(docs):
        print(f"{i+1}: Title: {doc['title']}")

asyncio.run(main())

# ──