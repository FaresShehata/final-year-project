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
        with open(file_path, "r", encoding="utf-8") as f:
            return cls.from_json(f.read(), **kwargs)


def get_serialisable_fields(model_type: type[pg.GenericAlias]) -> set[str]:
    """
    Get the fields of model_type that are marked as serialisable.
    """
    return {
        k
        for k, v in model_type.fields.items()
        if untyped(v.type) or issubclass(v.type, Serialisable)
    }


@rich.repr.auto
@attr.define(kw_only=True            "priority": self.priority.name,
            "status": self.status.value,
            "tags": self.tags,
            "title": self.title,
            "body": self.body,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()}

    @property
    def priority_name(self) -> str:
        return self._priority.name.lower()

    @staticmethod
    def _render_template(template_file_path: str, context: Context) -> str:
        template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader("."), autoescape=False
        )
        template = template_env.get_template(template_file_path)
        return template.render(context=context)

    def render_to_string(self, template_file_path: str) -> str:
        return self._render_template(template_file_path, context=self.context())


@attr.s
class Comment(Serialisable):
    id: int = attr.ib(validator=[validators.instance_of(int)])
    content: str = validator([validators.instance_of(str)])
    author_id: int = validator([validators.instance_of(int)])

    title: str | None = validator([optional(validators.instance_of(str))])
    body: str | None = validator([optional(validators.instance_of(str))])

    created_at: datetime.datetime = field(factory=datetime.datetime.now)
    updated_at: datetime.datetime = field(init=False, default_factory=lambda: self.created_at)

    tags: frozenset[str] = field(converter=set)
    status: Status = field(default=Status.PUBLISHED)
    priority: Priority = field(default=Priority.LOW)

    context: Context = field(default=Factory(Context))
    _serialise_attrs: tuple[str, ...] = field(
        init=False, default=("id", "content", "author_id", "tags", "status", "priority")
    )

    _priority: Priority = field(
        converter=Priority,
        metadata={"max_length": 50},
        default=Priority.MEDIUM,
    )


@rich.repr.auto
@attr.define(kw_only=True, slots=True)
class TodoItem(Serialisable):
    id: int = field(converter=int, factory=uuid.uuid4)
    title: str = field(validator=validators.instance_of(str))
    description: str | None = field(metadata=dict(default=None), validator=[optional(validators.instance_of(str))])
    completed: bool = field(default=False)
    due_date: Optional[date] = field(
        default=None, validator=Optional(validators.instance_of(date))
    )
    created_at: datetime.datetime = field(factory=datetime    ClassVar,
    Generic,
    Iterator,
    Literal,
    Protocol,
    TypeVar,
    overload,
    runtime_checkable,
)

if TYPE_CHECKING:
    from types import TracebackType


class AsyncIterator(Generic[T]):
    def __aiter__(self):
        return self

    @overload
    async def __anext__(self: AsyncIterator[None]) -> None:
        ...

    @overload
    async def __anext__(self: AsyncIterator[T]) -> T:
        ...

    async def __anext__(self):
        """Return the next item from the iterator."""
        raise NotImplementedError("An `AsyncIterator` must implement `__anext__()`")


@runtime_checkable
class SupportsLessThan(Protocol[T]):
    def __lt__(self, other: object) -> bool:
        ...


@dataclasses.dataclass(slots=True)
class User:
    name: str
    username: str
    email: str | None = None
    password: str | None = None
    age: int | None = None
    is_active: bool | None = True
    friends: list[str] = dataclasses.field(default_factory=list)

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise TypeError(f"{self.__repr__()}.name must be a string.")
        if not isinstance(self.username, str):
            raise TypeError(
                f"{self.__repr__()}.username must be a string."
            )
        if not isinstance(self.email, (str, type(None))):
            raise TypeError(f"{self.__repr__()}.email must be a string or None.")
        if not isinstance(self.password, (str, type(None))):
            raise TypeError(
                f"{self.__repr__()}.password must be a string or None."
            )
        if not isinstance(self.age, (int, type(None))):
            raise TypeError(f"{self.__repr__()}.age must be an integer or None.")
        if not isinstance(self.is_active, bool):
            raise TypeError(f"{self.__repr__()}.is_active must be a boolean.")

        self.friends.sort()


def get_random_user():
    while True:
        yield User(
            name=f"User {random.randint(1, 1_000_000)}",
            username=f"user_{random.randint(1, 1_000_000)}",
            email=f"user_{random.randint(1, 1_000_000)}@example.com",
            password="password",
