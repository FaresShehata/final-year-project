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


async def main_1():
    async with read_until_closed_v2(open_connection()) as reader:
        for line in reader:
            print(line)


# Python 3.6+
async def main_2():
    async with open_connection() as conn:
        async for line in conn:
            print(line)


# ── Coroutines ───────────────────────────────────────────────────────────────

class MyCoroutine:
    def __await__(self):
        yield


coroutine = coroutine_generator.send(None)

# The following call is equivalent to calling coroutine()
result = coroutine.__next__()
print(result)

result = coroutine.send("Hello!")
print(result)

result = coroutine.throw(ValueError("Invalid input"))
print(result)

try:
    result = coroutine.close()
except RuntimeError:
    print("cannot close once sent / thrown")

# To actually use a coroutine we need an event loop
loop = asyncio.new_event_loop()
task = loop.create_task(coroutine)
try:
    task.result()
finally:
    loop.run_forever()


# ── Generators ────────────────────────────────────────────────────────────────

def fibonacci(limit: int):
    current, nxt = 0, 1
    while current < limit:
        yield current
        current, nxt = nxt, current + nxt


for i in range(40):
    print(next(fibonacci(i)))


# ── Itertools ────────────────────────────────────────────────────────────────

def factorial(n: int) -> int:
    return n * factorial(n - 1) if n else 1


cache: dict[int, int] = {}


def memoized_factorial(n: int) -> int:
    if n not in cache:
        cache[n] = n * memoized_factorial(n - 1) if n else 1
    return cache[n]


factorial(4) == memoized_factorial(4)


# ── Comprehensions ────────────────────────────────────────────────────────────

cities = ["Berlin", 'Rome', "Prague"]
zip_codes = [80374, 00100, 1510]
country_code = ['DE', 'IT', 'CZ']


def cities_by_country(zip_codes, country_code):
    return {city: code for city, code in zip(cities, country_code)}


cities_by_country(zip_codes, country_code)
# => {"Berlin": "DE", "Rome": "IT
    def __init__(self, expected_type: type, lo=None, hi=None):
        self.expected_type = expected_type
        self.lo = lo
        self.hi = hi
        self.name: str = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = f"_{owner.__name__}__{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.name, None)

    def __set__(self, obj, value) -> None:
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.name}: expected {self.expected_type.__name__}, got {type(value).__name__}"
            )
        if self.lo is not None and value < self.lo:
            raise ValueError(f"{self.name}: {value} below minimum {self.lo}")
        if self.hi is not None and value > self.hi:
            raise ValueError(f"{self.name}: {value} above maximum {self.hi}")
        setattr(obj, self.name, value)


class CachedProperty:
    """Non-data descriptor implementing a lazy cached property."""

    def __init__(self, func):
        self.func = func
        self.attrname: Optional[str] = None
        functools.update_wrapper(self, func)

    def __set_name__(self, owner, name):
        self.attrname = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        cache = obj.__dict__
        val = cache.get(self.attrname, _MISSING)
        if val is _MISSING:
            val = self.func(obj)
            cache[self.attrname] = val
        return val


_MISSING = object()

# ── Metaclass ─────────────────────────────────────────────────────────────────

class RegistryMeta(abc.ABCMeta):
    """Metaclass that maintains a registry of all concrete subclasses."""

    @property
    def instances(cls) -> list[type]:
        return [val for _, val in vars(cls).items() if isinstance(val, type)]

    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        cls.instances.append(instance)
        return instance


def register(name: str = NoNameType) -> ClassVar:
    """
    Decorator for metaclass base classes.
    Adds class info to the registry.

    :param name: Name used when registering; defaults to the class's name
    """

    def wrapper(cls) -> ClassVar:
        if not hasattr(cls, "__subclasses"):
            cls.__subclasses__ = []
        if name != NoNameType:
            cls.__name__ = name
        cls.registry = cls.registry or {}
        cls.registry[name] = cls
        cls.__subclasses__.append(cls)
        return cls

    return wrapper


@register()
class BaseClass:
    pass

class Subclass(BaseClass): pass

BaseClass.instances  # => [<class '__main__.Subclass'>]


# ── Context manager ───────────────────────────────────────────────────────────

class RedirectionManager:

    def __enter__(self) -> ContextManager:
        old_stdout = sys.stdout
        sys.stdout = open("/dev/null", "w")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        sys.stdout.close()
        sys.stdout = old_stdout
        return False


with contextlib.ExitStack() as stack:
    with stack.enter_context(RedirectionManager()) as rdm:
        print(sys.version_info.major)

    print(stack._exits.keys())
    # => {'<ExitStack.exitafter>': <function ExitStack._check_exit at ...>}
    # => '<built-in function exit>'


# ── Generators ───────────────────────────────────────────────────────────────

def count(n: int) -> Generator[int, None, None]: ...
