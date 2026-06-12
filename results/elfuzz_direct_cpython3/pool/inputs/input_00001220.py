"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import datetime as dt
import hashlib
import os.path
from collections.abc import Awaitable, Callable, Coroutine
from functools import wraps
from io import BytesIO
from pathlib import Path
from typing import Any, TypeVar

T = TypeVar("T")
U = TypeVar("U")


async def fetch(url: str) -> bytes:
    """Fetch the given url and return its content."""
    print(f"Fetching {url}")
    await asyncio.sleep(1)
    return b"This is an example response!"


# Wraps a function to make it async.
def async_wrap(func: Callable[..., T]) -> Callable[..., Awaitable[T]]:
    @wraps(func)
    async def run(*args: Any, **kwargs: Any) -> T:
        # Get the coroutine returned by func().
        coro: Coroutine[Any, Any, T] = func(*args, **kwargs)

        # Wrap the coroutine in an `Awaitable` and then await the result.
        return await coro

    return run


@async_wrap
async def download(url: str, path: Path | None = None) -> None:
    """Download the file at the given URL and save it to disk.

    If no path is provided, use the filename from the URL.
    """
    if not path:
        path = Path(os.path.basename(url))
    data = await fetch(url)
    with open(path, "wb") as f:
        f.write(data)


class MyString(str):
    pass


def hash_me(my_string: MyString) -> str:
    return hashlib.sha1(my_string.encode()).hexdigest()


# This will be allowed because we have a type hint for my_string.
result = hash_me(MyString("Hello World"))

# This will raise a TypeError because our type hint does not match.
result = hash_me("Hello World")


# This will also be allowed because methods are first-class citizens.
download = async_wrap(download)


if True:
    download = async_wrap(download)


#
# Python's standard library provides several useful methods for working with strings.
#

# The built-in `str` object supports various operations such as concatenation (`+`),
# repetition (`*`), slicing (`[]`) and more. However, unlike many other types in Python,
# `str` objects cannot be used as keys in dictionaries or sets.


print("\b\b\b")

# When using `str`, you need to take care when working with Unicode characters that may require
# proper encoding methods like UTF-8.


def strip_punctuation(string: str) -> str:
    # Removes all punctuation from the string.
    return ''.join(c for c in string if c.isalnum())


assert strip_punctuation('Hello, World!') == 'HelloWorld'


# To work around this issue, you can create a custom class called `MyString` that inherits from `str`.
# Then you can define additional methods on this new class. For instance, you could add a method that checks
# if a string contains only alphanumeric characters:

class MyString(str):
    def is_alphanumeric(self) -> bool:
        return self.isalnum()

# Now, you can call this method directly on instances of `MyString` without any issues:


my_string = MyString('Hello, World!')
print(my_string.is_alphanumeric())  # Prints True


#
# Functions with default arguments
#


def greeting(name: str = "Guest") -> str:
    return f"Hello, {name}!"


print(greeting())

# You can also specify a default value for keyword-only arguments. Keyword-only arguments must be specified after positional-only arguments.
# For example, let’s say you want to implement a logging function that takes three parameters: the log level, the message, and a callback function to handle the log messages.


def logger(level: str, message: str, callback: Callable[[str], None] = lambda msg: print(msg)):
    callback(message)


logger('INFO', 'This is an info message')

# It’s important to note that keyword-only arguments should always come after positional-only arguments when defining a function signature.


# In the above example, the `callback` argument is a callable that accepts a single string parameter and returns nothing. By specifying `callback: Callable[[str], None]`,
# we indicate that the `callback` argument expects a callable thatimport pathlib
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
    Annotated, Callable, ClassVar, Concatenate, Coroutine, DefaultDict, Dict, Generator, Generic, Literal,
    NamedTuple, NonEmptySequence, ParamSpec, Protocol, Sequence, Set, Tuple, TypedDict, Union, cast)
from types import TracebackType
from typing_extensions import Self, TypeAlias, TypeGuard, Unpack, get_args, get_origin, get_type_hints
from collections.abc import AsyncGenerator, Awaitable


def _test_str():
    print('type: str')
    s1 = 'Hello world.'
    print(s1)
    s2 = """Hello\nworld."""
    print(s2)
    
    print('\nstring formatting:')
    print('{name} has {age} years.'.format(name='John', age=37))
    print(f'{name} has {age} years.')
    
    print('\nbuilt-in methods:')
    print(type(s1.upper()))
    print(repr(s1.title()))
    print(len(s1))
    print(sorted(set(s1)))
    
    
    print('\nmethods with default arguments:')
    def func(arg: str = '') -> str:
        return arg
    
    print(func())
    print(func(arg='arg'))
    

def _test_repr():
    print('\nrepr() and str():')
    x = 123
    y = str(x).upper()
    print(y)
    z = str(x + int(str(10))).title()
    print(z)
    a = repr(y + z).replace("'", '"').strip('"') # type: ignore[assignment]
    print(a)


def _test_format():
    print('\nstring.format():')
    name = 'John'
    age = 37
    print('{} has {} years.'.format(name, age))
    print('{name} has {age} years.'.format(age=age, name=name))


def _test_unary_operators():
    print('\nunary operators:')
    print(~ - ~+ - (- + ~))
    print(+ - ~ + ~- -- + ++ --++ ----)
    print((~ + - ~ + - ~ + - ~) + (~ - - - - - - - - - - - - -))
    print(
        ((~ + - ~ + - ~ + - ~) + (~ - - - - - - - - - - - - -)) +
        (((~ + - ~ + - ~ + - ~) + (~ - - - - - - - - - - - - -)) -
         (~ + - ~ + - ~ + - ~ + - ~ + - ~ + - ~ + - ~ + - ~ + - ~ + - ~ + - ~ + - ~ + - ~ + - ~ + - ~ + - ~))
    )
    print(f'({binascii.unhexlify("ffff")}){pow(-1, 1)}')


def _test_binary_operators():
    print('\nbinary operators:')
    print(binhash(10, 20), binhash(10, 20    Yields:
        A descriptor of each class in the hierarchy, left-to-right.

    Examples:
        >>> class Base1: ...
        >>> class Base2: ...
        >>> class Sub(Base1): ...
        >>> class SubSub(Sub, Base2): ...
        >>> class SubSubSub(SubSub): ...
        
        >>> list(iter_dfs(Base1)) == [Base1]
        True
        
        >>> list(iter_dfs(SubSubSub)) == [SubSubSub, SubSub, Sub, Base2, Base1]
        True
        
    """
    if obj is None:
        yield from ()
    elif is_descriptor(obj):
        yield obj.__origin__
        yield obj.__member__
    else:
        yield obj
        for subclass in getattr(obj, "__subclasses__", tuple()):
            yield from iter_dfs(subclass)


