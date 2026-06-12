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
        if obj is None:
            return self
        return getattr(obj, self.name, None)

    def __set__(self, obj, value) -> None:
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.name}: expected {self.expected_type.__name__}, got {type(value).__name__}"
            )
        if self.lo is not None and value < self.lo:
            raise ValueError(f"{self.name}: {value} below minimum {self.lo}")
        if self.hi is not None and value > self.hi:
            raise ValueError(f"{self.name}: {value} above maximum {self.hi}")
        setattr(obj, self.name, value)


class CachedProperty:
    """Non-data descriptor implementing a lazy cached property."""

    def __init__(self, func):
        self.func = func
        self.attrname: Optional[str] = None
        functools.update_wrapper(self, func)

    def __set_name__(self, owner, name):
        self.attrname = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        cache = obj.__dict__
        val = cache.get(self.attrname, _MISSING)
        if val is _MISSING:
            val = self.func(obj)
            cache[self.attrname] = val
        return val


_MISSING = object()

# ── Metaclass ─────────────────────────────────────────────────────────────────

class RegistryMeta(abc.ABCMeta):
    """Metaclass that maintains a registry of all concrete subclasses."""
    
    @classmethod
    def __prepare__(metacls, clsname, bases): # pylint: disable=unused-argument
        return super().__prepare__(clsname, bases)
    
    def __new__(metacls, clsname, bases, clsdict):
        cls = super().__new__(metacls, clsname, bases, clsdict)
        cls._registry.append(cls)
        return cls
    
    @property
    def registry(cls) -> list[type]:
        return cls._registry or []
    
    _registry: ClassVar[list[type]] = []


# ─── Custom Types ─────────────────────────────────────────────────────────────

class SortedList(list):

    def sort(self,
             key=lambda x: x,
             reverse=False,
             /,
             *,
             keyfunc=str.casefold,
             ascending=True,
             case_sensitive=False,
             ):
        # TODO: refactor to support multiple keys
        return sorted(super().copy(), key=key, reverse=reverse)

    def insert_sorted(self,
                      index: int,
                      item: T,
                      key=lambda x: x,
                      reverse=False,
                      /,
                      *,
                      keyfunc=str.casefold,
                      ascending=True,
                      case_sensitive=False,
                      ):
        return self.insert(index, key(item))


# ── Decorators ────────────────────────────────────────────────────────────────

def deprecated(reason: str) -> Callable[..., Any]:
    """
    Marks function as deprecated.

    Args:
        reason (str): Reason for deprecation.
    """

    assert reason.startswith("\n"), "reason must start with newline"

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        call_args = inspect.signature(func).bind_partial(*sys.argv[1:])
        call_args.apply_defaults()
        params = call_args.arguments
        msg = (
            f"\n\n\tDEPRECATION WARNING:\n"
            f"\tFunction '{params['func']}' has been deprecated.\n"
            f"\tReason: {reason}\n"
        )

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            print(msg, file=sys.stderr)
            return func(*args, **kwargs)

        return wrapper

    return decorator


# ── Context Managers ───────────────────────────────────────────────────────────

class DuplicateError(Exception):
    pass


class ContextManager:

    def __enter__(self):
        ...
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        ...


class Singleton(type):

    instances: dict[Any, Any] = {}

    def __call__(cls, *args, **kwargs):
        try:
            instance = cls.instances.pop(cls)
        except KeyError:
            instance = super().__call__(*args, **kwargs)
            cls.register(instance)
        return instance
    
    @staticmethod
    def register(instance: Any) -> None:
        cls = instance.__class__
        cls.instances[cls] = instance


class ThreadLocalContext(metaclass=Singleton):

    thread_local_var: set[int] = weakref.WeakKeyDictionary()

    def __init__(self) -> None:
        self.thread_local_var.clear()

    def push(self, value: int) -> None:
        self.thread_local_var[threading.current_thread()] = value

    def pop(self) -> None:
        del self.thread_local_var[threading.current_thread()]

       Protocol,
    TypeVar,
    overload,
    runtime_checkable,
)

if TYPE_CHECKING:
    pass  # keep TYPE_CHECKING branch exercised

K = TypeVar("K")
V = TypeVar("V")
T = TypeVar("T")

# ── Enums ─────────────────────────────────────────────────────────────────────

class Status(enum.Enum):
    PENDING   = "pending"
    RUNNING   = "running"
    SUCCESS   = "success"
    FAILED    = "failed"
    CANCELLED = "cancelled"

    def is_terminal(self) -> bool:
        return self in {Status.SUCCESS, Status.FAILED, Status.CANCELLED}


class Priority(enum.IntEnum):
    LOW    = 1
    NORMAL = 5
    HIGH   = 10
    URGENT = 20


class Flag(enum.Flag):
    READ    = enum.auto()
    WRITE   = enum.auto()
    EXECUTE = enum.auto()
    RWX     = READ | WRITE | EXECUTE


# ── Protocols ─────────────────────────────────────────────────────────────────

@runtime_checkable
class Serialisable(Protocol):
    def to_dict(self) -> dict: ...

    @classmethod
    def from_dict(cls, data: dict) -> "Serialisable": ...


@runtime_checkable
class Runnable(Protocol):
    async def run(self) -> str: ...


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(order=True, frozen=False, slots=True)
class Point:
    x: float
    y: float

    def distance(self, other: Point) -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


@dataclasses.dataclass
class Task:
    id: int
    name: str
    priority: Priority = Priority.NORMAL
    status: Status = dataclasses.field(default=Status.PENDING)
    tags: list[str] = dataclasses.field(default_factory=list)
    metadata: dict = dataclasses.field(default_factory=dict)
    _history: list[Status] = dataclasses.field(default_factory=list, repr=False)

    # comparison key ignores status
    sort_key: int = dataclasses.field(init=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "sort_key", -int(self.priority))

    def transition(self, new_status: Status) -> None:
        self._history.append(self.status)
        self.status = new_status

    def to_json(self) -> str:
        return json.dumps({
