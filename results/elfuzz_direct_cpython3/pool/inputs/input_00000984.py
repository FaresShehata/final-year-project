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

class NonNegativeInteger(Annotated[int, numbers.Integral, numbers.Number]):
    def __post_init__(self): ...


class PositiveFloat(Annotated[float, numbers.Real, numbers.Number]):
    def __post_init__(self): ...


# ── New-style classes with type hints ────────────────────────────────────────

class Allocator(Generic[T]):

    class Resource:
        pass

    def acquire(self) -> Resource:
        return self.Resource()

    def release(self, resource: Resource):
        del resource

    def allocate_many(self, count: NonNegativeInteger) -> list[Resource]:
        return [self.acquire() for _ in range(count)]
    
    def release_many(self, resources: Sequence[Resource]):
        for r in reversed(resources):
            self.release(r)


# ── TypeVar aliases and new-style class design patterns ──────────────────────

ModelType: TypeVar('ModelType')

def model_factory(model_class: Type[ModelType]) -> ModelFactory[ModelType]:
    """Create a factory function for creating instances of `model_class`."""
    def create_model(**kwargs: KWArgs) -> ModelType:
        if not isinstance(kwargs, kwargs_typedict):
            raise TypeError(f"create_model() got unexpected keyword arguments {list(kwargs)}")
        if any(k not in model_class.__annotations__.keys() for k in kwargs.keys()):
            raise ValueError(f"{model_class} has the following attributes: "
                             f"{', '.join(sorted(model_class.__annotations__))}")
        return model_class(**kwargs)
        
    return create_model


class ModelFactory(Generic[ModelType]):
    def __call__(self, **kwargs: KWArgs) -> ModelType:
        return self.create_model(**kwargs)


KWArgs: TypeVar("KWArgs", bound=Mapping[str, Any])

# ── Reveal types ────────────────────────────────────────────────────────────

reveal_type(123)
reveal_type([1, 2])
reveal_type((1, 2))
reveal_type({1, 2})
reveal_type({"a": 1})
reveal_type((lambda x: x)(1))
reveal_type(lambda x: x(x))(1)
reveal_type([] + [])
reveal_type([])
reveal_type(None)
reveal_type(True)
reveal_type(False)
reveal_type(None == False)
reveal_type(type(None))

# ── contextlib suppress ────────────────────────────────────────────────────

with contextlib.suppress(ValueError):
    raise ValueError

try:
    raise ValueError
except Exception as e:
    with contextlib.suppress(Exception):
        raise e

# ── contextlib redirect_output ──────────────────────────────────────────────

@contextlib.redirect_stdout(io.StringIO())
def foo():
    print("Hello world!")
foo()
print(sys.stdout.getvalue())

# ── contextlib redirect_stderr ──────────────────────────────────────────────

@contextlib.redirect_stderr(io.StringIO())
def bar():
    print("Error!", file=sys.stderr)
bar()
print(sys.stderr.getvalue())

# ── contextlib contextmanager ─────────