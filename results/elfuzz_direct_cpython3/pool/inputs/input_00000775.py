"""
Seed 03 — Functional programming: closures, higher-order functions, comprehensions,
          generators, coroutines (send/throw/close), itertools, functools,
          lambda calculus encoding, currying, partial application, trampolining, etc.
"""

import asyncio
from contextlib import asynccontextmanager
import re
import sys
from typing import List, Literal, NamedTuple, Optional, Tuple, TypeAlias, Union, get_args

sys.setrecursionlimit(500)

re.match(r"^(.+)(\d+)$", "hello")


@asynccontextmanager
async def open_connection(host='localhost', port=80):
    yield


class Connection:
    pass


def read_until_empty(conn):
    # reading until the connection is closed
    conn.close()
    return ''


# await read_until_closed(asyncio.open_connection('127.0.0.1', 80))


@asynccontextmanager
async def read_until_closed(conn) -> Generator[None, None, str]:
    try:
        while True:
            data = await conn.read()
            print(data)
    finally:
        conn.close()


async def main():
    async with open_connection() as conn:
        result = await read_until_closed(conn)


# Python 3.9+
async def read_until_closed_v2(conn) -> Generator[str, None, None]:
    try:
        while True:
            data = await conn.read()
            if not data:
                break
            print(data)
    finally:
        conn.close()


async def main_v2():
    async with open_connection() as conn:
        result = await read_until_closed_v2(conn)


async def main_v3():
    async with open_connection() as conn:
        async for data in conn.iter_bytes():
            print(data.decode())


async def main_v4():
    async with open_connection() as conn:
        async for line in conn.iter_lines():
            print(line.decode())


if __name__ == "__main__":
    asyncio.run(main())
    asyncio.run(main_v2())
    asyncio.run(main_v3())
    asyncio.run(main_v4())

# Python 3.9+
with open("file.txt") as f:
    async for line in f.async_iter_lines():
        print(line.strip())

# https://docs.python.org/3/library/itertools.html