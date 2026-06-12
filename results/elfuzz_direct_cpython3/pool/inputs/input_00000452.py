"""
Seed 01 — OOP, metaclasses, descriptors, decorators, context managers, generators
"""

from __future__ import annotations

import abc
import contextlib
import functools
import json
import logging
from collections.abc import Generator, Iterable, Iterator
from enum import Enum
from typing import TYPE_CHECKING, Any, Generic, TypeVar

import attr
import attr.validators as validators
import jinja2
import jinja2.exceptions
import jinja2.meta
import pydantic
import pydantic.generics as pg
import rich.repr
import typed_ast.ast3
from attrs import Factory, define, field
from attr.converters import optional
from typed_ast.ast3 import AST
from typing_extensions import Self

if TYPE_CHECKING:
    from concurrent.futures import Future


logger = logging.getLogger(__name__)

_T = TypeVar("_T")


@define
class Context:
    """A context for rendering templates."""


def untyped(obj: object) -> bool:
    """Whether `obj` is typed."""
    try:
        return not obj.__class__.__annotations__.get("__type_comment__")
    except AttributeError:  # pragma: no cover
        return True


@rich.repr.auto
@attr.s(slots=True)
class Serialisable(metaclass=abc.ABCMeta):
    """An object that can be serialised to JSON.

    This interface is meant to provide a common base class contract.
    """

    @property
    @abc.abstractmethod
    def _serialise_attrs(self) -> tuple[str, ...]:
        ...

    def json(self, **kwargs: Any) -> str:
        kwargs.setdefault("default", lambda x: getattr(x, "_json", repr(x)))
        return json.dumps(self.dict(), **kwargs)

    def dump(self, file_path: str, **kwargs: Any) -> None:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.json(**kwargs))

    @classmethod
    def load(cls, file_path: str, **kwargs: Any) -> Self | None:
        with open(file_path, "rb") as f:
            data = f.read()
        return cls.parse_obj(
            data,
            strict=False,
            allow_inf_nan=False,
            use_enum_values=True,
            keep_undefined_fields=False,
            **kwargs,
        )

    def update(
        self,
        other: Self | dict[str, Any] | Iterable[tuple[str, Any]],
        *,
        filter_none: bool = False,
    ) -> None:
        if isinstance(other, (dict, type(self))):
            return super().update(other, filter_none=filter_none)
        elif isinstance(other, (list, set)):
            raise TypeError(f"{other=} must be an iterable of pairs.")
        else:
            items = (
                other
                if isinstance(other, tuple)
                else ((k, v) for k, v in other.items())
            )
            return super().update(items, filter_none=filter_none)

    def dict(
        self,
        *,
        recurse: bool = False,
        exclude: Iterable[str] | dict[str, Any] | type[Serialisable] = (),
        value_filter: Callable[[Any], Any] | None = None,
    ) -> dict[str, Any]:
        """Return the object's internal data representation as a dictionary, or its
        ``_asdict`` method's output, depending on whether this object is serializable."""
        if isinstance(exclude, (tuple, set)) and (
            has := any(isinstance(e, type(self)) for e in exclude)
        ):
            exclude = {e.__class__.__qualname__: e for e in exclude}
        elif isinstance(exclude, dict) and has:
            exclude.update((e.__class__.__qualname__, e) for e in exclude.values())

        if recurse and hasattr(self, "_asdict"):
            data: dict[str, Any] = {}
            if isinstance(value_filter, type(lambda: ...)):
                value_filter = value_filter
            elif value_filter is None:
                value_filter = lambda _: _
            for k, v in sorted(self._asdict().items()):
                if k.endswith("_generator"):
                    continue
                data[k] = (
                    self._recursive_serialize(v, exclude, value_filter)
                    if recurse
                    else v
                )
            return data

        if isinstance(exclude, type(self)):
            exclude = exclude.__qualname__
        elif isinstance(exclude, dict):
            exclude = tuple(sorted(exclude.keys()))
        else:
            exclude = tuple    def __repr__(self) -> str:
        return f"SortedList({self._data!r})"


# ── Async machinery ───────────────────────────────────────────────────────────

