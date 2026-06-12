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


if __name__ == '__main__':
    asyncio.run(main())