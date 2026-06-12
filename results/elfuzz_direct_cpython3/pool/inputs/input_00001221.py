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

# ── Descriptors ──────────────────────────────────────────────────────────────--


def annotated_from_hint(cls : type) -> type:
    """Decorator that converts typed dicts into subtypes with type checks."""
    cls_dict = cls.__dict__

    @functools.wraps(cls)
    class TypedCls:
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._validate()

        def __setattr__(self, key, val):
            try:
                allowed_types = cls_dict[key].__annotations__["value"]
            except KeyError:
                super().__setattr__(key, val)
            else:
                if not isinstance(val, allowed_types):
                    raise TypeError(
                        f"{cls.__name__}.{key} must be {allowed_types}"
                    )
                super().__setattr__(key, val)

        def _validate(self):
            for field, hint in get_type_hints(cls).items():
                assert hasattr(self, field), (
                    f"missing attribute {field!r} in {cls.__name__}"
                )

    return TypedCls


def Annotated(*constraints):
    """Decorator that adds a "constraint" metadata field to the target."""
    def wrapper(target):
        target.__metadata__ = list(hint for hint in constraints)
        return annotated_from_hint(target)
    return wrapper


def get_type_hints(cls : type, *, include_extras=True):
    """
    Get type annotation from a Python class.

    Args:
      cls: The class.
      include_extras: Include extraneous annotations.

    Returns:
        A dictionary mapping names of attributes to their types.
    """
    if not include_extras:
        # We use `vars` instead of `_fields` because with non-strict
        # annotations we might have extra fields.
        return vars(cls).copy()
    return {
        key : val.annotation
        for key, val in iter_fields(cls)
        # with non-strict annotations we might have extra fields,
        # so we skip them here with `include_extras=False`.
        if val.annotation != Ellipsis
    }


# ── Generators ────────────────────────────────────────────────────────────────


def batched(iterable, n):
    """Batch data into tuples of length n. The last batch may be shorter."""
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while batch := tuple(itertools    email:    str
    active:   bool
    metadata: dict[str, Any]


class MetricsRecord(TypedDict):
    latency_ms: float
    throughput: float
    error_rate: float


# ── Annotated constraints (runtime-checked via descriptor) ───────────────────

class _Constrained:
    """Descriptor that reads Annotated metadata to validate."""

    def __set_name__(self, owner, name):
        self.pub  = name
        self.priv = f"_{owner.__name__}__{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.priv, None)

    def __set__(self, obj, value):
        hints = get_type_hints(type(obj), include_extras=True)
        ann   = hints.get(self.pub)
        if ann and hasattr(ann, "__metadata__"):
            for constraint in ann.__metadata__:
                if callable(constraint):
                    if not constraint(value):
                        raise ValueError(f"{self.pub}={value!r} fails constraint")
        setattr(obj, self.priv, value)

def positive_int(x: int) -> None:
    if x <= 0:
        raise ValueError("positive integer required")


class PositiveInt(_Constrained):
    pass

PositiveInt.__metadata__ = [positive_int]


class NonNegativeFloat(_Constrained):
    pass

NonNegativeFloat.__metadata__ = [lambda x : isinstance(x, float) and x >= 0.0]


class MaxLength(str): # pylint: disable=too-few-public-methods
    """String with a maximum length."""

    def __new__(cls, s : str, max_length : int):
        if len(s) > max_length:
            raise ValueError(f"length {len(s)} exceeds {max_length}")
        return super().__new__(cls, s)


MaxLength.__metadata__ = [
    lambda validator : lambda v : isinstance(v, str) and len(v) <= validator(max_length=v),
    lambda validator : validator(max_length=20),
]


# ── TypedDict subclass example (TypeVar + _Constraint) ───────────────────────

class Record(Generic[T]):
    name: str
    value : T

class MetricRecord(Record[MetricsRecord]):
    pass

metric_record : MetricRecord = MetricRecord(name="foo", value={"latency_ms": 1})
print(metric_record.value.latency_ms)


# ── TypedDict with _Constraint examples (TypeVar + _Constraint) ──────────────

@Annotated.from_hint(MetricRecord)
class MetricRecord_1:
    name: str
    value : MetricsRecord

record_1 : MetricRecord_1 = MetricRecord_1(name="bar", value={"latency_ms": 2})
print(record_1.value.latency_ms)


