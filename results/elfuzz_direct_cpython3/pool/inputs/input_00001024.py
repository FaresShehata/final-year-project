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

class UserRecord(TypedDict, total=False):
    id:       int
    name:     str
    email:    str
    active:   bool
    metadata: dict[str, Any]


class MetricsRecord(TypedDict):
    latency_ms: float
    throughput: float
    error_rate: float


# ── Annotated constraints (runtime-checked via descriptor) ───────────────────

class _Constrained:
    """Descriptor that reads Annotated metadata to validate."""

    constraint: tuple[Any, ...]
    args:       tuple[int, int]

    def __init__(self, annotation: type[_Constrained], *args: Any, **kwargs: Any) -> None:
        self.constraint = kwargs.pop("_constraint", ())
        self.args = args
        super().__init__(annotation, *args, **kwargs)

    @property
    def _name(self) -> str:
        return str(type(self)).split("'")[1].split(".")[-1]

    def __get__(self, obj: Any, cls: type[Any]) -> Any:
        result = getattr(obj, "_" + self._name, None)
        if result is None:
            raise AttributeError(
                f"No such attribute '{self._name}' "
                f"in instance of type {type(cls).__qualname__}",
            )
        return result

    def __set__(self, obj: Any, value: Any) -> None:
        expected_types = [t.__origin__ for t in self.constraint]
        fail_msg = (
            f"'{value}' ({type(value)}) does not match one of the following types: "
            + ", ".join([t.__name__ for t in expected_types])
        )

        if any(isinstance(value, tp) for tp in expected_types):
            setattr(obj, "_" + self._name, value)
            return

        raise TypeError(fail_msg)

    def __repr__(self) -> str:
        return repr(getattr(self, "_name")) + "." + super().__repr__()



@Annotated[
    _Constrained[int, int],
    "This value must be an integer between 1 and 10",
]
def constrained_function(x: int) -> None:
    pass



# ── ParamSpec ─────────────────────────────────────────────────────────────────

ParamSpec1: TypeAlias = ParamSpec["ParamSpec1"]
ParamSpec2: TypeAlias = ParamSpec["ParamSpec2"]


def foo(*a: ParamSpec1, **kw: ParamSpec2) -> None:
    ...


foo(1, x="abc", y=2.5)
foo(1, 2, 3, {"x": "y"})  # Error!


# ── Concatenate ───────────────────────────────────────────────────────────────

Concatenate[T, Tuple[X]]: TypeAlias = T | Tuple[X]


x: Concatenate[int, str] = 1234
y: Concatenate[float, str] = "hello"




# ── TypeAlias aliases ─────────────────────────────────────────────────────────

TypeAlias1: TypeAlias = Annotated[int, "A description"]

TypeAlias2: TypeAlias = Concatenate[Literal["a"], Literal["b"]]
TypeAlias3: TypeAlias = Union[int, str, Tuple[TypeAlias1, TypeAlias2]]

TypeAlias4: TypeAlias = Annotated[TypeAlias3, "description"]

TypeAlias5: TypeAlias = Annotated[TypeAlias4, "another description"]





# ── TypedDict attributes ──────────────────────────────────────────────────────

UserRecord["id"]: int

UserRecord["metadata"]["address"]["street"]: str






# ── Class method override ────────────────────────────────────────────────────

class MyDict(dict):
    def get(self, key: str, default=None) -> Any:
        try:
            return super().get(key)
        except KeyError:
            return default

MyDict.get("key", "default_value")  # OK!
# MyDict().get("key", "default_value")  # Error!



class MyList(list):
    def pop(self, index=-1) -> Any:
        try:
            return super().pop(index)
        except IndexError:
            return None

MyList().pop()  # OK!
# MyList(["a"]).pop(0)  # Error!

# ── Type checking with get_type_hints ─────────────────────────────────────────

def func(x: str | float) -> float:
    return x / 2

get_type_hints(func) == {
    "__return__: float",
}
reveal_type(func(3))  # Revealed type is 'builtins.float'
reveal_type(func("two"))  # Reveled type is 'builtins.float'



# ── A class with a private field ──────────────────────────────────────────────

class MyClass:
    _private_field: int

    def set_private_field(self, value: int) -> None:
        self._private_field = value

    def get_private_field(self) -> int:
        return self._private_field

my_instance = MyClass()

# my_instance._private_field = 10  # Error! Can't access the private field.
print(my_instance.get_private_field())  # OK.


# ─import weakref
from typing import Any

# ── Bytecode introspection ────────────────────────────────────────────────────

def annotated_disassembly(fn) -> str:
    buf = io.StringIO()
