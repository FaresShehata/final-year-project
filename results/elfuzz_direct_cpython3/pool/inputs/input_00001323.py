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


class SingletonMeta(type):
    """
    Metaclass that makes a class behave like a singleton.
    """

    _instances: dict[type[object], object] = {}

    def __call__(cls: type[Singleton]) -> Singleton:
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__()
        return cls._instances[cls]


class Singleton(metaclass=SingletonMeta):
    """"""""

    def __new__(
        mcs: type[Singleton],
        name: str,
        bases: tuple[type[Any], ...],
        namespace: dict[str, Any],
        **kwargs: Any
    ) -> Singleton:
        cls = super().__new__(mcs, name, bases, namespace)
        instance: Singleton | None = sys.modules.get(cls.__module__, None)

        # If there already exists a Singleton subclass for the current module,
        # replace it with the newly created Singleton subclass. Otherwise,
        # assign the new Singleton subclass to the module-level attribute.
        if instance is not None:
            setattr(sys.modules[cls.__module__], name, cls)
        else:
            instance = cls()
        cls._instance = instance
        return instance

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class SingletonDerived(Singleton):
    """"""


@contextlib.contextmanager
def open_context_manager(path: str) -> Generator[None, None, None]:
    print(f"Opening file '{path}'...")
    try:
        yield
    finally:
        print(f"Closing file '{path}'...")


# ── Meta-classes ───────────────────────────────────────────────────────────────


class CountCalls(type):
    _counter: int = 0

    def __call__(cls, *args: Any, **kwds: Any) -> CountCalls:
        cls._counter += 1
        instance: CountCalls = super().__call__(*args, **kwds)
        print(f"{instance} instantiated {CountCalls._counter} times")
        return instance


class Spam(metaclass=CountCalls):

    @classmethod
    def get_instance_count(cls: type[Spam]) -> int:
        return cls._counter


print(Spam(), Spam())
print(Spam.get_instance_count())

# ╔═══════════════════════════════════════════════════════════╗
# ║                                                        ║
# ║                      Factory Methods                     ║
# ║                        -------------------                ║
# ║                                                        ║
# ╚═══════════════════════════════════════════════════════════╝
# A factory method is not actually a function#         ...
# --------------------------------------------------------
# This will allow your code to check whether instances of your classes conform
# to this protocol at runtime, without requiring them to be checked at compile
# time.

# ─────────────────────────────────────────────────────────────────────────────
#
# You can also define an abstract base class (ABC) that acts as a protocol using
# the abc module:

from abc import ABCMeta, abstractmethod

class IMyProtocol(metaclass=ABCMeta):
    @abstractmethod
    def my_method(self) -> None:
        ...

# ─────────────────────────────────────────────────────────────────────────────
#
# The third option is to use the 'typing_extensions' module's '_ProtocolMetaclass'.
# This meta-class provides similar functionality to the 'runtime_checkable'
# decorator but allows for the creation of generic protocols, which were not
# possible with the original _Protocol metaclass.

from typing_extensions import _ProtocolMetaclass

class IMyGenericProtocol(_ProtocolMetaclass[T]):
    @abstractmethod
    def my_method(self, x: T) -> None:
        ...

# ─────────────────────────────────────────────────────────────────────────────
#
# Note that these approaches provide different levels of support for type hints
# and static type checking:
#
# * Using the 'runtime_checkable' decorator or the 'abc' module ensures that
#   type-checking errors are raised during development.
# * Defining an ABC or using the '_ProtocolMetaclass' for generic protocols may
#   improve performance by allowing the implementation of concrete methods, but
#   it comes with limitations regarding the use of generic types within those
#   protocols.
