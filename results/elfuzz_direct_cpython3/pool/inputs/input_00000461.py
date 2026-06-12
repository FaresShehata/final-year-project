"""
Seed 01 — OOP, metaclasses, descriptors, decorators, context managers, generators
"""

from __future__ import annotations

import abc
import contextlib
import functools
import itertools
import operator
import sys
import types
import weakref
from typing import Any, ClassVar, Generator, Iterator, Optional, Type, TypeVar

T = TypeVar("T")

# ── Descriptors ──────────────────────────────────────────────────────────────

class TypedDescriptor:
    """Descriptor that enforces a type and optional range constraint."""

    def __init__(self, expected_type: type, lo=None, hi=None):
        self.expected_type = expected_type
        self.lo = lo
        self.hi = hi
        self.name: str = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = f"_{owner.__name__}__{name}"

    def __get__(self, obj, objtype=None):
        value = getattr(obj, self.name)
        if not isinstance(value, self.expected_type):
            raise TypeError(f"{value!r} must be an instance of {self.expected_type}")
        if self.lo is not None and value < self.lo:
            raise ValueError(f"{value} less than minimum allowed ({self.lo})")
        if self.hi is not None and value > self.hi:
            raise ValueError(f"{value} greater than maximum allowed ({self.hi})")
        return value

    def __set__(self, obj, value):
        setattr(obj, self.name, value)


# ── Meta classes ──────────────────────────────────────────────────────────────

class TypedMeta(type):
    def __new__(cls, name: str, bases: tuple[type], namespace: dict[str, Any]):

        if "__slots__" in namespace:
            pass

        for attr_name, attr_value in namespace.items():
            if isinstance(attr_value, TypedDescriptor):
                attr_value.name = attr_name

        return super().__new__(cls, name, bases, namespace)


class MyClass(metaclass=TypedMeta):

    my_attr: str

# ── Context Managers ───────────────────────────────────────────────────────────

def context_manager(func: Callable[..., Optional[Awaitable[T]]]) -> Callable[..., T]:

    def wrapper(*args, **kwargs) -> T:
        with ContextManager() as cm:
            result = func(*args, **kwargs)
            if result is not None:
                yield result
            else:
                yield cm.result()

    return wrapper


class ContextManager(contextlib.AbstractContextManager):

    def __init__(self) -> None:
        self.result: Optional[Any] = None  # private attribute
        # TODO: Add support for exception handling
        # https://docs.python.org/3/reference/datamodel.html#index-74

    def __enter__(self) -> "ContextManager":
        print("Entering the context manager.")
        return self

    def __exit__(
        self, exc_type: Optional[type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[types.TracebackType]
    ) -> Optional[bool]:
        print("Exiting the context manager.")
        # Return True if you want to suppress the exception.
        # If False, the exception will be propagated out of the block.


@contextmanager
def foo_context_manager(): ...
with foo_context_manager() as foo: ... 
from __future__ import annotations

import asyncio
import dataclasses
import functools
import inspect
import logging
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import fields
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Generic,
    List,
    Literal,
    NamedTuple,
    NoReturn,
    Optional,
    Tuple,
    Union,
)

if TYPE_CHECKING:
    from .core import LoggingConfig, ParsedLoggingConfig

logger = logging.getLogger(__name__)


def _is_iterable(val: Any) -> bool:
    """
    Returns True if val is iterable (but not strings).
    """
    try:
        iter(val)
    except Exception:
        return False
    else:
        return not isinstance(val, str)


def _flatten_nested_values(
    nested_vals: Iterable[Any],
    item_is_iterable_fn=_is_iterable,
    filter_none=True,
    skip_first_level=False,
) -> List[Any]: ...


class DictToNamedTuple(NamedTuple): ...
DictToNamedTuple._make(...)

DICT_TO_NAMED_TUPLE_TYPES = {
    int: int,
    float: float,
    complex: complex,
}
named_tuple_fields: Dict[NamdedTupleType, FieldInfo]

for key, value in DICT_TO_NAMED_TUPLE_TYPES.items():
    field_info = FieldInfo(key=key, default_factory=value)
    named_tuple_fields[key] = field_info

field_infos_per_named_tuple_type: Dict[NamdedTupleType, List[FieldInfo]]

for nt in NamedTupleTypes.values():
    nt.field_infos = [
        *itertools.chain.from_iterable([fi.default_factory for fi in nt.fields])
    ]
    field_infos_per_named_tuple_type[nt] = [fi for fi in nt.field_infos]


class Pipe(Generic[T]): ...
Pipe.__parameters__

pipe_1 = Pipe[int]()
pipe_2 = pipe_1 | 2 + 2

pipe_3 = pipe_2 & lambda x: x + 5
pipe_4 = pipe_3 << 6


class Extractor(Generic[T]):
    def __call__(self, obj: T) -> T: ...


class FilterExtractor(Extractor[Tuple[T, bool]]): ...
FilterExtractor.__parameters__
extracted_data = filter_extractor(extracted_data)

filter_result = filter_extractor(result)
filter_results = list(filter(lambda r: r[1], extracted_data))


class PipelineResult(Generic[T]): ...


class Pipeline(Typed