"""
Seed 03 — Functional programming: closures, higher-order functions, comprehensions,
          generators, coroutines (send/throw/close), itertools, functools,
          lambda calculus encoding, currying, partial application, trampolining
"""

from __future__ import annotations

import functools
import itertools
import operator
import sys
import time
from collections.abc import Callable
from typing import Any, Awaitable, Callable


async def main() -> None:
    print(f"1. {time.time()} seed03.py")

    async def read_stream(stream_name: str) -> AsyncGenerator[str, None]:
        """Return a coroutine that reads from the given stream."""
        for line in iter(lambda: await stream_name.readline(), ""):
            yield line.rstrip()

    stream = read_stream(sys.stdin)

    # streams are iterable too!
    async for data in stream:
        print(data)

    # streams can be used as arguments to other coroutines.
    # this is useful when reading files or stdin.
    async with open("seed02.txt") as stream:
        async for data in stream:
            print(data)

    # both of these return an iterator over string lines.
    # but the first one yields each line individually.
    # the second one returns a string that contains all lines joined by newlines.
    async def get_file_lines(file_path: str) -> AsyncIterator[str] | str:
        with open(file_path) as file:
            return "\n".join(itertools.islice(file, 5))

    file_lines = await get_file_lines("seed02.txt")
    print(type(file_lines))
    if isinstance(file_lines, str):
        print(file_lines)
    else:
        for line in file_lines:
            print(line.strip())

    # the second example shows how you can use async for loops
    # to iterate over the contents of an asynchronous generator such as `read_stream`.
    # tuple unpacking syntax helps here because it allows us to assign multiple variables at once.
    # we also don't have to convert the result into a list before using zip function.
    # and we can use any number of elements in the zip pattern.
    async for host, port in zip(
        ("localhost", "example.com"), range(80, 90)
    ):
        print(host, port)

    # callables can be passed as parameters just like regular functions
    async def do_twice(func: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        for _ in range(2):
            await func(*args, **kwargs)

    # await do_twice(read_stream, "data.txt")

    # built-in zip function takes two iterators and returns an iterator over tuples.
    # however our custom implementation doesn't work well with infinite iterators.
        await stream.send("9")
        await stream.send("q")

    print("done.")


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    finally:
        loop.close()


