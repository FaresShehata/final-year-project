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

    def __set__(self, obj, val):
        if not isinstance(val, self.expected_type):
            raise TypeError(
                f"Expected {self.expected_type}, got {val!r}"
                "(expected type)"
            )
        if self.lo and val < self.lo:
            raise TypeError(
                f"Got {val!r}, which falls below range ({self.lo})"
            )
        if self.hi and val > self.hi:
            raise TypeError(
                f"Got {val!r}, which exceeds the range ({self.hi}) "
            )

        setattr(obj, self.name, val)


def typed(name: str) -> type:
    """
    Returns a new descriptor class with a single attribute named after self.

    The attribute is set by setting an instance of this descriptor on the target
    object. This can be done using the dot notation, or through calling it as a
    function (and passing the instance as first argument).

    >>> from pprint import pprint
    >>>
    >>> class Foo(object):
    ...     bar = typed('bar')
    ...
    >>>
    >>> pprint(Foo.bar)
    <some random object>

    If one wants to enforce specific values, they need to define the attributes
    `lo` and `hi`, e.g.

    >>> class Bar(object):
    ...     baz = typed('baz', lo=3, hi=7)
    ...
    >>>
    >>> pprint(Bar.baz)
    <some random object>
    """

    self = TypedDescriptor()
    self.name = ""
    return self


class TypedGenericMeta(type):
    def __new__(mcls, name, bases, namespace):

        attrs = {
            attr: TypedDescriptor() for attr in namespace.keys()
            if not attr.startswith("_")
        }
        return super().__new__(mcls, name, bases, namespace.update(attrs))

    # def __call__(cls, *args, **kwargs):
    #     instance = super().__call__(*args, **kwargs)
    #     for k, v in kwargs.items():
    #         setattr(instance, k, v)

    def __getitem__(cls, args):
        """Returns a subclass of cls that uses the given parameters."""

        if isinstance(args, tuple) and len(args) == 2:
            lo, hi = args

            class New(cls, metaclass=TypedGenericMeta):
                lo = lo
                hi = hi

            return New

        elif isinstance(args, int):
            class New(cls, metaclass=TypedGenericMeta):
                lo = -sys.maxsize
                hi = args

            return New

        else:
            raise TypeError(f"{type(self).__name__}[...] invalid")


# ── Mixins ───────────────────────────────────────────────────────────────────

class BaseMetaclass(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def data(self) -> dict[str, Any]:
        pass

    @data.setter
    @abc.abstractmethod
    def data(self, value: Any) -> None:
        pass

    @classmethod
    @abc.abstractmethod
    def get_instance(cls, key: str) -> T | BaseMetaclass:
        pass

    @property
    @abc.abstractmethod
    def instances(self) -> dict[str, BaseMetaclass]:
        pass

    @instances.setter
    @abc.abstractmethod
    def instances(self, value: dict[str, BaseMetaclass]) -> None:
        pass

    @classmethod
    @abc.abstractmethod
    def get_instances(cls) -> dict[str, BaseMetaclass]:
        pass

    @classmethod
    @abc.abstractmethod
    def add_instance(cls, instance: BaseMetaclass) -> None:
        pass


class BaseClass(BaseMetaclass):
    data: dict[str, Any] = {}
    instances: dict[str, BaseMetaclass] = {}

    @staticmethod
    def get_instance(key: str) -> BaseMetaclass:
        return BaseMetaclass.instances[key]

    @property
    def instances(self) -> dict[str, BaseMetaclass]:
        return BaseMetaclass.instances

    @instances.setter
    def instances(self, value: dict[str, BaseMetaclass]):
        BaseMetaclass.instances = value

    @classmethod
    def get_instances(cls) -> dict[str, BaseMetaclass]:
        return cls.instances

    @classmethod
    def add_instance(cls, instance: BaseMetaclass):
        cls.instances[instance.key] = instance


class SubclassOfDict(dict, metaclass=BaseMetaclass):
    pass


class BasesFromList(list, metaclass=BaseMetaclass):
    pass


class EmptyClasses(object):
    pass


class Singleton(object):
    _instance: Singleton | None = None

    def __new__(cls, *args, **kwds):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__new__(
                cls, *args, **kwds
            )
        return cls._instance


@contextlib.contextmanager
def assert_raises(exc_class: type[Exception]):
    try:
        yield
    except Exception as exc:
        if not isinstance(exc, exc_class):
            raise AssertionError(f"Expected exception of type {exc_class}")
    else:
        raise AssertionError(f"No exception was raised")


# ── Generators ───────────────────────────────────────────────────────────────

def gen_func(n: int) -> Generator[int, None, None]:
    counter = 0
    while True:
        counter += n
        yield counter


def fib_gen(a: int = 0, b: int = 1) -> Generator[int, None, None]:
    while True:
        yield a
        a, b = b, a + b


def fibo_gen() -> Generator[int, None, None]:
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def all_even(iterable: Iterable[int]) -> Generator[int, None, None]:
    for i in iterable:
        if i % 2else:

    def make_adder_from_bytecode(delta: int) -> types.FunctionType:
        pass


class Mode(enum.Enum):
    default = enum.auto()
    debug = enum.auto()


_MODE = Mode.default
_TIME_FUNCTION = bool(os.environ.get("TIME_FUNCTION", False))
del os, enum


# ── High-level functions ──────────────────────────────────────────────────────

LARGE_INTS = [
    9_567_983_233_547_022_263,
    -9_567_983_233_547_022_263,
]
LARGE_FLOATS = [
    9_567_983_233_547_022_263.432,
    -9_567_983_233_547_022_263.432,
]


def sum_odd_squares(
    start: int = LARGE_INTS[0],
    stop: int = LARGE_INTS[-1],
    delta: int = 2,
) -> int:
