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
    connection = Connection()
    try:
        yield connection
    finally:
        connection.close()


class Connection:
    def close(self):
        pass


class Table(NamedTuple):
    name: str
    rows: int


def table_exists(name: str) -> bool:
    for table in tables:
        if table.name == name:
            return True
    else:
        return False


tables = []


async def drop_table(name: str):
    if table_exists(name):
        # do stuff
        tables.remove(Table(name, len(tables)))
    else:
        raise ValueError(f'table "{name}" does not exist')


async def create_table(name: str):
    if not table_exists(name):
        # do stuff
        tables.append(Table(name, len(tables)))
    else:
        raise ValueError(f'table "{name}" already exists')


# ─────────────────────────────────────────────────────────────────────────────

# 📖  https://realpython.com/python-lambda/

lambda hello: 'world'

(lambda x: x * x)(4)

((lambda x: x ** 2 / x)(4))

(lambda x, y: x + 2 + y)(4, 6)
(lambda x: x ** 2)(4)

lambda hello: 'world'  # <function <lambda> at 0x7f7e938956b0>
(lambda x: x * x)(4)  # 16
((lambda x: x ** 2 / x)(4))  # 4.0
(lambda x, y: x + 2 + y)(4, 6)  # 12
(lambda x: x ** 2)(4)  # 16

# ─────────────────────────────────────────────────────────────────────────────

# 📖  https://docs.python.org/3/tutorial/classes.html


def add(x, y):
    """Adds two numbers and returns the result."""
    return x + y


add.__doc__  # Add two numbers and return their sum.

        return n
    return fib_async(n-1) + fib_async(n-2)


async def fib_iter_async():
    yield 1
    if n := await fib_async(1): yield n
    i = 1
    while True:
        if n := await fib_async(i): yield n
        i += 1


# ── Walrus Operator ───────────────────────────────────────────────────────────

a, b = 1, 2
x = (c := a + b, a := b, b := c)[-1]


# ── Pattern Matching ──────────────────────────────────────────────────────────

match ["apple"]:
    case []:
        print("empty")
    case ["apple"] as fruit:
