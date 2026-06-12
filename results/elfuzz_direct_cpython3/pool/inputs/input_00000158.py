"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import datetime as dt
import hashlib
import os.path
from collections.abc import Awaitable, Callable, Coroutine
from functools import wraps
from io import BytesIO
from pathlib import Path
from typing import Any, TypeVar

T = TypeVar("T")
U = TypeVar("U")


async def fetch(url: str) -> bytes:
    """Fetch the given url and return its content."""
    print(f"Fetching {url}")
    await asyncio.sleep(1)
    return b"This is an example response!"


# Wraps a function to make it async.
def async_wrap(func: Callable[..., T]) -> Callable[..., Awaitable[T]]:
    @wraps(func)
    async def run(*args: Any, **kwargs: Any) -> T:
        # Get the coroutine returned by func().
        coro: Coroutine[Any, Any, T] = func(*args, **kwargs)

        # Wrap the coroutine in an `Awaitable` and then await the result.
        return await coro

    return run


@async_wrap
async def download(url: str, path: Path | None = None) -> None:
    """Download the file at the given URL and save it to disk.

    If no path is provided, use the filename from the URL.
    """
    if not path:
        path = Path(os.path.basename(url))
    data = await fetch(url)
    with open(path, "wb") as f:
        f.write(data)


class MyString(str):
    pass


def hash_me(my_string: MyString) -> str:
    return hashlib.sha1(my_string.encode()).hexdigest()


# This will be allowed because we have a type hint for my_string.
result = hash_me(MyString("Hello World"))

# This will raise a TypeError because our type hint does not match.
result = hash_me("Hello World")

# The following methods are available on dataclasses that do not have fields marked with default_factory=staticmethod.
# https://docs.python.org/3/library/dataclasses.html#default-factories
data = {"key": "value"}
d = data["key"]
print(d)  # value