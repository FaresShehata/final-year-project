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

JsonDict: TypedDict(
    "JsonDict",
    {
        str: "Union[int, float, str, bool, None, List['JsonDict']]"
        # or ValueType
    }
)

# ── Enum ─────────────────────────────────────────────────────────────────────

enum_class: Final[tuple[type[Any], ...]] = (
    FileNotFoundError,
    MemoryError,
    NotImplementedError,
    RuntimeError,
)


# ── class_getitem ───────────────────────────────────────────────────────────

def _call_type_hint(typehint: type[T]) -> None:
    """Placeholder function for type hint call."""

    return isinstance(typehint(), T)
TypeHintCall = Callable[[type[T]], None]


def _get_missing_typehints(cls: type[Any]) -> set[type[Any]]:
    missing = {t for t in cls.__annotations__.values() if not issubclass(t, type)}

    for base in cls.__bases__:
        missing |= _get_missing_typehints(base)

    return missing


_missing_typehints: ClassVar[set[type[Any]]] = _get_missing_typehints(Enum)


@contextlib.contextmanager
def typecheck(cls: type[Any]) -> Iterator[None]:
    """
    Context manager that checks whether all type hints are satisfied by the
    instance being created.
    """

    errors = []

    def check_type_hint(key: str, value: Any) -> None:
        try:
            if not issubclass(value, type):
                raise TypeError(f"Invalid typehint '{key}'")

        except Exception as ex:
            errors.append(ex)

    with get_type_hints(cls) as typehints:
        for key, value in typehints.items():
            if value not in (_missing_typehints | enum_class):
                check_type_hint(key, value)

    if errors:
        raise TypeError("\n".join(str(error) for error in errors))

    yield


# ── get_type_hints ───────────────────────────────────────────────────────────

def _annotated_is_annotated(annotated: type[Any]) -> bool:
    return hasattr(annotated, "__origin__") and annotated.__origin__ == Annotated


def _annotated_get_args(annotated: type[Any]) -> tuple[type[Any], ...]:
    origin = getattr(annotated, "__origin__", object)

    if origin != Annotated:
        raise ValueError("Must be an 'Annotated' type.")
    else:
        args = getattr(annotated, "__args__")

        if len(args) < 2:
            raise ValueError("Requires at least two arguments.")

        return args


def _annotate_arg(arg: type[Any], annotation: type[Any]) -> type[Any]:
    if arg in enum_class:
        return arg
    elif _annotated_is_annotated(annotation):
        return _annotate_arg(annotation, annotation.__args__[0])
    else:
        return annotation


def _replace_annotation(func: Callable[..., T], annotation: type[Any]) -> Callable[..., T]:
    args = func.__code__.co_varnames[:func.__code__.co_argcount]
    sig = inspect.signature(func).bind_partial(*args, **{"return": annotation})

    def wrapper(*args_: tuple[Any, ...], **kwargs: Mapping[str, Any]) -> T:
        return func(*sig.arguments.values(), **sig.kwargs)

    return cast(Callable[..., T], wrapper)


def _combine_annotations(
    func: Callable[P, T],
    annotations: Mapping[str, type[Any]],
    annotation: type[Any],
) -> Callable[P, T]:
    if not _annotated_is_annotated(annotation):
        annotations = {**annotations, *((_annotate_arg(a, annotation), a) for a in annotations.values())}
    elif annotation in enum_class:
        annotations = {**annotations, *((a, annotation) for a in annotations.values())}

    return _replace_annotation(func, annotation=annotation.get_origin() | annotations)


def get_type_hints_with_annotations(obj: Any) -> Mapping[str, type[Any]]:
    """Returns type-hints of `obj`, but also includes annotations applied on fields."""
    hints_obj = get_type_hints(obj)
    hints_cls = get_type_hints(type(obj))
    annotations = {}

    for name, field in obj.__dict__.items():
        if name.startswith("__"):
            continue

        if field.annotation is Ellipsis:
            new_field = field.replace(annotation=object())
        elif isinstance(field.annotation, Annotated):
            new_field = field.replace(annotation=field.annotation.get_origin() | field.annotation.__args__)
        else:
            new_field = field._replace(annotation=None)

        if new_field.name in hints_cls:
            new_field = new_field.replace(annotation=hints_cls[new_field.name])

        if new_field.name in hints_obj:
            new_field = new_field.replace(annotation=hints_obj[new_field.name])

        annotations[name] = new_field.annotation

   