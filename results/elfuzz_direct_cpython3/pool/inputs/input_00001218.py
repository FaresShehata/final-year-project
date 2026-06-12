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

    @classmethod
    @abc.abstractmethod
    def _serialise_defaults(cls) -> dict[str, str | int | float | None]:
        ...

    def serialise(self) -> dict[str, Any]:  # noqa: A003
        """Serialise this instance to JSON."""

        result = {key: getattr(self, key) for key in self._serialise_attrs}

        defaults = self._serialise_defaults()
        for key, value in defaults.items():
            if key not in result and value is not None:
                result[key] = value

        return result

    @staticmethod
    def deserialise(data: dict[str, Any]) -> Serialisable:
        """Deserialise data into an instance of the subclass."""
        cls = type(data)

        template = jinja2.Template(
            f"""{% set {", ".join(f"{k}=data.get({repr(k))})" for k in {cls._serialise_attrs)}}\n{cls.__init__.__code__.co_name}({", ".join([f"{v}" for v in locals().values()])})""",
            undefined=jinja2.StrictUndefined,
        )
        try:
            return template.render(**data)
        except jinja2.exceptions.UndefinedError as err:
            raise ValueError("Invalid data") from err


@rich.repr.auto
@attr.s(repr=False, slots=True, frozen=True)
class Deserialisable(Serialisable):
    """A deserialisable object."""

    @classmethod
    def _deserialise_class_names(cls, classnames: list[str]) -> list[type[Self]]:
        """Get a list of classes corresponding to the given class names."""
        module_path, _, name = cls.__module__, cls.__qualname__, ""
        module_globals = vars(globals()[module_path])

        for classname in classnames:
            partname, *_ = classname.split(".")
            name += "." + partname
            if (subcls := module_globals.get(partname)) is None or not isinstance(subcls, type):
                continue

            if subcls.__bases__[0].__module__ == "builtins":
                continue

            if (qualname := f"{cls.__module__}.{subcls.__qualname__}") != name:
                logger.debug(f'Found "{qualified_class_name}", expected "{name}".')
                continue

            break

        else:
            raise ValueError("Could not find any sub-class with matching name")

        return [subcls]

    @classmethod
    def _deserialise_subclasses(cls, subclassnames: list[str]) -> list[type[Self]] | None:
        """Get a list of all subclasses of the given class names."""
        found = []
        module_path, _, name = cls.__module__, cls.__qualname__, ""
        module_globals = globals()
        module_globals.update(vars(module_globals))

        for classname in subclassnames:
            partname, *_ = classname.split(".")
            name += "." + partname
            if qualname := f"{module_path}.{classname}":
                if (subcls := module_globals.get(qualname)) is not None and isinstance(subcls, type):
                    if subcls.__bases__[0].__module__ == "builtins":
                        continue

                    if (subcls_qualname := f"{cls.__module__}.{subcls.__qualname__}") != name:
                        logger.debug(f'Found "{qualified_class_name}", expected "{name}".')
                        continue

                    found.append(subcls)
                elif (subcls_module_globals := subcls.__globals__) is not None:
                    subcls_module_globals.update(vars(subcls_module_globals))
                    for subpartname, subpartvalue in subcls_module_globals.items():
                        if (
                            subpartname.startswith(name)
                            and subpartname.endswith(classname)
                            and (subclass := type(subpartvalue)) is not None
                            and subclass.__module__ == module_path
                            and subclass.__qualname__ == name
                        ):
                            found.append(subclass)

        if len(found) > 1:
            raise ValueError("Multiple matches for subclass")

        return found or None

    @classmethod
    @abc.abstractmethod
    def _des