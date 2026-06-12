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
    """"""


class SimpleDescriptor:
    """Simple descriptor."""

    owner_class: ClassVar[Type[Any]]

    def __set_name__(self, owner: Any, name: str) -> None:
        self.owner_class = type(owner)
        self.name = name

    def __get__(self, instance: Any, owner: Type[Any]) -> Any:
        if instance is None:
            return self
        result = getattr(instance.__dict__, self.name)
        setattr(instance.__dict__, self.name, self.owner_class(result))
        return result


@functools.cache
def cached_property(fun: Callable[..., T]) -> PropertyWrapper:
    """Decorator for caching property values."""
    return PropertyWrapper(name=fun.__name__, fun=fun)


class PropertyWrapper:
    """Class to hold information about cached properties."""

    def __init__(self, *, name: str, fun: Callable[..., T]):
        self.name = name
        self.fun = fun

    def __get__(self, instance: Any, owner: Type[Any]) -> T:
        assert isinstance(self.name, str)
        value = self.fun(instance)
        return value


# ─── Context Managers ────────────────────────────────────────────────────────


class FileContextManager:
    """A file context manager.

    The ``with`` statement can be used with this class to manage opening and closing of files.
    """

    def __init__(self, filename: str, mode: str) -> None:
        self.filename = filename
        self.mode = mode
        self.file: Optional[IO[Any]] = None

    def open_file(self) -> IO[Any]:
        return open(self.filename, mode=self.mode)

    def close_file(self) -> None:
        if self.file is not None:
            self.file.close()

    def __enter__(self) -> IO[Any]:
        print(f"Opening {self.filename}...")
        self.file = self.open_file()
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb) -> Optional[bool]:
        print(f"Closing {self.filename}...") 
        self.close_file()
        return False


class AnotherFileContextManager(FileContextManager):
    """Another file context manager. This one closes the file after reading it contents."""

    def __getattr__(self, attr: str) -> Any:
        if attr == "__exit__":
            raise AttributeError("Cannot override magic methods!")
        else:
            return super().__getattr__(attr)

    def read_contents(self) -> str:
        return self.file.read()


@contextlib.contextmanager
def get_context_manager(filename: str, mode: str) -> Generator[IO[str], None, None]:
    """Function that returns a context manager that opens and closes a file."""
    try:
        yield FileContextManager(filename, mode)
    finally:
        pass


@contextlib.contextmanager
def another_get_context_manager(
    filename: str,
    mode: str,
    line_endings: Literal["dos", "unix", "mac"]
) -> Generator[IO[str], None, None]:
    """This function also returns a context manager but closes the file before yielding it."""
    try:
        yield AnotherFileContextManager(filename, mode)
    finally:
        pass


@contextlib.contextmanager
def open_file_with_leading_whitespace_and_trailing_newline():
    f = open('somefile.txt', 'r+')

    line_list = [line.rstrip('\n') + '\n' for line in f.readlines()]

    f.seek(0)   # rewind
    f.writelines(line_list)

    f.truncate()  # remove any extra whitespace at end of file
    
    try:
        yield f
    finally:
        f.close()


@contextlib.contextmanager
def open_connection():
    connection = sqlite3.connect(":memory:")
    cursor = connection.cursor()
    try:
        yield (connection, cursor)
    finally:
        cursor.close()
        connection.close()


@contextlib.contextmanager
def fetch_table(cursor: Cursor) -> Generator[tuple[list[str], list[tuple]], None, None]:
    cursor.execute('SELECT * FROM users;')
    rows = cursor.fetchall()
    cols = [column[0] for column in cursor.description]
    yield (cols, rows)


@contextlib.contextmanager
def fetch_results(results: Iterable[Row]) -> Generator[tuple[str, ...], None, None]:
    keys = results[        break
        
async with open_connection() as conn:  # Use the `async` keyword when calling an `async` method.
    await create_table("test3")
    await insert_row("test3", 1, 'one', 2, 'two', 3, 'three')  
    await insert_row("test3", 11, 'eleven', 21, 'twenty-one', 31, 'thirty-one')
    
    async for row in select_all_rows(["field3", "field1", "row_id"]):
        assert row[0] == 'three'
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
        self.name: str = "" # TODO: Implement this field.

    def __set_name__(self, owner: type[T], name: str) -> None:
        self.name = name

    def __set__(self, instance: T, value: Any) -> None:
        if not isinstance(value, self.expected_type):
            raise TypeError(f"Expected {self.expected_type}")
        
        if self.lo is not None and value < self.lo or \
           self.hi is not None and value > self.hi:
