"""
Type hints as described here are a subset of the full Python 3.8 specification.
See https://docs.python.org/3/library/typing.html#module-contents ."""

from typing import *
import sys
from collections.abc import Iterable
from functools import partial
from inspect import signature
from itertools import chain, repeat
from operator import itemgetter
from random import randint
import re
import time
from types import UnionType
from warnings import warn as warning

if sys.version_info >= (3,9):
    from collections.abc import Callable as Callable_T
else:
    from typing_extensions import Literal as Literal_T
    from typing_extensions import Protocol as Protocol_T
    from typing_extensions import TypedDict as TypedDict_T
    from typing_extensions import TypeAlias as TypeAlias_T
    from typing_extensions import Concatenate as Concatenate_T
    from typing_extensions import ParamSpec as ParamSpec_T
    from typing_extensions import Self as Self_T
    from typing_extensions import ForwardRef as ForwardRef_T
    from typing_extensions import NotRequired as NotRequired_T

    class Protocol_T(Protocol): pass
    class TypedDict_T(TypedDict): pass
    class ForwardRef_T(FutureWarning): pass
    class NotRequired_T(DeprecationWarning): pass
    class Concatenate_T(DeprecationWarning): pass
    class ParamSpec_T(DeprecationWarning): pass
    class Self_T(DeprecationWarning): pass

from unicodedata import (
    category,
    normalize,
)

from rich.console import ConsoleRenderable
from rich.highlighter import Highlighter
from rich.style import Style
from rich.text import Text

try:
    from rich.pretty import Pretty
except ImportError:
    """pretty module not available on pypy"""
    def Pretty(obj: Any) -> str:  # pragma: no cover
        return repr(obj)

class PrettyHighlighter(Highlighter):

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self._highlighters = dict()
        self._colordict = {'<': '#A0522D', '>': '#2E8B57'}

    def highlight(self, text: Text, style: Style) -> Text:
        if len(text) > 64:
            text = '...' + text[-61:]
        try:
            h = self._highlighters[text]
        except KeyError:
            h = self._highlighters.setdefault(
                text,
                Pretty(text).style(style)
            )
        return h


def _isunbounded(s: Any) -> bool:
    return s is Ellipsis or isinstance(s, slice) and s.start is Ellipsis

__all__ = [
    "Any",
    "Callable", "TypeVar", "Union", "Optional",
    "Literal", "_isunbounded", "Unpack",
]

Any = Any  # type: ignore[assignment] # mypy bug

TypeVar = TypeVar
"""Type variable."""

Union = Union
"""Union type."""

Optional = Optional
"""Optional type."""

Literal = Literal
"""Literal type."""

ParamSpec = ParamSpec_T  # to match python 3.10
"""Parameter specification."""
Concatenate = Concatenate_T  # to match python 3.10
"""Concatenate type."""

Unpack = Unpack  # to match python 3.10
"""Unpack type."""

Self = Self_T  # to match python 3.10
"""Type for representing an instance of its own type."""

ForwardRef = ForwardRef_T  # to match python 3.10
"""Forward reference.

.. versionadded:: 3.9
"""


@overload
def partial(func: Callable[..., T], /, *args: Any, **keywords: Any) -> Callable[[Tuple[Any, ...]], T]: ...
@overload
def partial(func: Callable[..., T], /, keywords: Dict[str, Any]) -> Callable[[Tuple[Any, ...]], T]: ...

def partial(func: Callable[..., T], /, *args: Any, **keywords: Any) -> Callable[[Tuple[Any, ...]], T]:
    if not args and not keywords:
        return func
    if keywords.get('func') == func and all(isinstance(arg, (tuple, list)) for arg in args):
        return partial(func.__wrapped__, *(chain.from_iterable(args)), **{k:v for k,v in keywords.items() if v is not None})
    else:
        return partial(func.__wrapped__, *args, **keywords)


def setdefault(d: MutableMapping[T, U], key: K, default_factory: Callable[[], V]) -> Tuple[MutableMapping[T, U], V]:
    if key in d:
        return d, d[key]
    else:
        new_key = default_factory()
        d[key] = new_key
        return d, new_key


def getitem(x: Mapping[K, V], key: K) -> Optional[V]:
    try:
        return x[key]
    except (KeyError, IndexError):
        return None


class CacheMeta(type):
    """
    Metaclass that creates a cache property on classes whose first argument
    is the keyword ``cache``::

         class Foo(metaclass=CacheMeta):
             @property
             @cache
             def bar(self, baz):
                 ...

    This decorator requires the decorated function to be memoizeable using
    :func:`functools.lru_cache`. It will only work with functions taking at most
    one positional argument. The positional argument will be unpacked into
    the cache's arguments when accessed via the attribute accessor. If no
    arguments are passed, nothing is cached.

    .. note::
       Caching is currently implemented by storing the entire result in memory
       which can quickly grow large depending on the size of objects stored
       inside it, especially if they are non-hashable. Caching should probably
       not be used with mutable types such as lists or dicts.

    .. versionchanged:: 3.9
       Added support for unbound methods.
    """

    def __new__(mcls, name, bases, namespace, *, cache=False):
        cls = super(CacheMeta, mcls).__new__(mcls, name, bases, namespace)