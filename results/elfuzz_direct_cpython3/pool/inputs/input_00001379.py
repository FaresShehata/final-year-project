"""
Seed 05 — Concurrency (threading/multiprocessing/concurrent.futures),
          string parsing (ast.literal_eval, tokenize, textwrap, string.Formatter),
          typing extras (TypedDict, ParamSpec, Concatenate, TypeAlias, Never,
          Annotated, get_type_hints, reveal_type stub),
          __class_getitem__, __set_name__, __init_subclass__,
          contextlib (suppress, redirect_stdout, AbstractContextManager),
          numbers ABC, pathlib, tempfile, csv, base64, hashlib, hmac, secrets
"""

from __future__ import annotations

import ast
import base64
import binascii
import csv
import hashlib
import hmac
import io
import itertools
import multiprocessing
import numbers
import os
import pathlib
import queue
import secrets
import string
import tempfile
import textwrap
import threading
import time
import tokenize
import contextlib
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import (
    Annotated,
    Any,
    Callable,
    ClassVar,
    Final,
    Generic,
    Literal,
    NamedTuple,
    Never,
    ParamSpec,
    TypeAlias,
    TypedDict,
    TypeVar,
    get_type_hints,
)

T  = TypeVar("T")
P  = ParamSpec("P")

# ── TypeAlias ────────────────────────────────────────────────────────────────

JsonValue: TypeAlias = "int | float | str | bool | None | list[JsonValue] | dict[str, JsonValue]"
Seconds:   TypeAlias = float
Predicate: TypeAlias = Callable[[Any], bool]

# ── TypedDict ────────────────────────────────────────────────────────────────

class User(TypedDict):
    username: str
    password: str
    is_awesome: bool

# ── ParamSpec ────────────────────────────────────────────────────────────────

def foo(*args: P.args, **kwargs: P.kwargs) -> tuple[P.args, P.kwargs]:
    ...

def bar(x: int, y: str = 'y', z: float = .123) -> float:
    return x + (y or "") + str(z)
print(get_type_hints(bar))

# ── Annotated ────────────────────────────────────────────────────────────────

Annotated[int, ...]
Annotated[int, ..., "Some docstring"]

@dataclasses.dataclass
class MyClass(Annotated[int]):
    a: int
    b: Annotated[float, "A fixed value"]
    c: Annotated[float, ..., 3.14]

# ── get_type_hints ──────────────────────────────────────────────────────────

def my_func(a: Annotated[int]) -> Annotated[int]: ...
get_type_hints(my_func)

# ── reveal_type ──────────────────────────────────────────────────────────────

reveal_type(int())

# ── ClassVar ────────────────────────────────────────────────────────────────

class Foo(ClassVar[int]): ...

Foo: int = 1

# ── _X__dict__() ────────────────────────────────────────────────────────────

class A:
    def __x_dict__(self) -> dict[str, Any]:
        return {"foo": self.foo}

class B(A):
    def __x_dict__(self) -> dict[str, Any]:
        return {"bar": super().__x_dict__()}

b = B()
b.__x_dict__()

# ── _X__init__() ────────────────────────────────────────────────────────────

class X(Generic[T]):
    def __init__(self, t: T) -> None:
        self.t: T = t

x = X[int]()
x.t == 1

# ── _X__new__() ──────────────────────────────────────────────────────────────

class Y(Generic[T]):
    def __new__(cls, *args: object, **kwargs: object) -> T:
        return cls._inner_new(cls, *args, **kwargs)

    @staticmethod
    def _inner_new(cls: type[Y[Any]], *args: object, **kwargs: object) -> Y[Any]:
        obj = Y[Any]._make_instance(cls, args, kwargs)
        obj.__init__(*args, **kwargs)
        return obj

    def __init__(self, *args: object, **kwargs: object) -> None:
        ...

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({", ".join(map(str, self.__dict__.values()))})'

y = Y[int](1, 2, 3)
assert isinstance(y, Y[int])
assert isinstance(y, Y[Any])

# ── __class_getitem__() ──────────────────────────────────────────────────────

class Z(Generic[T]):
    def __class_getitem__(cls, item: type[T]) -> type[Z[T]]:
        assert isinstance(item, type)
        return cls[item]

z: Z[int] = Z[int]
assert issubclass(z, Z[int])


class W(Generic[T]):
    def __class_getitem__(cls, item: Union[type[T], Tuple[type[T]]]) -> type[W[T]]:
        if isinstance(item, type):
            item = (item,)
        assert all(isinstance(i, type) for i in item)
        return cls[item]

w: W[int] = W[int]
assert issubclass(w, W[int])

# ── __set_name__() ──────────────────────────────────────────────────────────

class MyProperty:
    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

class MyDataclass:
    prop = MyProperty()

obj = MyDataclass()
assert obj.prop.name == 'prop'


class CustomNamedTuple(NamedTuple):
    x: int
    y: int

CustomNamedTuple(x=1, y=2)

# ── __init_subclass__() ──────────────────────────────────────────────────────

class MyMeta(type):
    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)

class MySubclass(metaclass=MyMeta): ...

MySubclass()


# ── Base
import ast
import base64
import binascii
import csv
import hashlib
import hmac
import io
import itertools
import multiprocessing
import numbers
import os
import pathlib
import queue
import secrets
import string
import tempfile
import textwrap
import threading
import time
import tokenize
import contextlib
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import (
    Annotated,
    Any,
    Callable,
    ClassVar,
    Final,
    Generic,
    Literal,
    NamedTuple,
    Never,
    ParamSpec,
    TypeAlias,
    TypedDict,
    TypeGuard,
    Union,
)
from types import ModuleType
from typing_extensions import Concatenate, get_args, get_origin, get_type_hints, get_type_hints_strict, is_typeddict, overload


def seed1() -> None:
    """Example: Context Manager with `with`."""
    with open('test.txt', 'w') as f:
        print('Hello World!', file=f)

    # if the context manager does not contain a return statement, it will implicitly return None.
    with open('test.txt', 'r') as f:
        pass

    try:
        with open('does-not-exist.txt', 'r') as f:
            pass
    except FileNotFoundError as e:
        print(e)


class ExampleClass:
    def __enter__(self):
        self.file = open('example.txt', 'w')
        return self

    def write(self, content: str) -> int:
        return self.file.write(content + '\n')

    def close(self):
        self.file.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            print(f'An error occurred while writing to example.txt. Error type: {exc_type}, error value: {exc_val}')
        else:
            print('Successfully wrote to example.txt.')


# This works similar to how you would use `with`, but in this case we're using it for a custom class.
with ExampleClass() as example_class:
    example_class.write('This is an example of how to use the context manager.')
    example_class.write('This another line of text.')


@contextlib.contextmanager
def example_context_manager() -> Iterator[str]:
    yield 'This is an example of how to use a context manager.'


with example_context_manager() as result:
    print(result)


@overload
def add(a: int, b: int) -> int: ...
@overload
def add(a: float, b: float) -> float: ...
def add(a: int | float, b: int | float) -> int | float:
    return a + b


print(add(2, 3))  # Returns 5
print(add(2.5, 3.7))  # Returns 6.2


class ExampleAsyncClass:
    async def __aenter__(self):
        self.file = open('example_async.txt', 'w')
