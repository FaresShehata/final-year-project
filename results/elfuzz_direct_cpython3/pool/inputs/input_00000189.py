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


if sys.platform.startswith("win"):
    import msvcrt

    def raw_input(prompt: Optional[str]=None) -> str:
        msvcrt.putch(b"\r\n")
        return input()


class LazyProperty(property):
    """
    Property that's evaluated only once per instance and then replaces itself with an ordinary attribute.

    This allows you to have properties do things like lazy-loading DB models without having to put the logic inside
    the property itself.

    Example:

        >>> class Dog:
        ...     name = LazyProperty(lambda self: "Spot")

        >>> d = Dog()
        >>>        if obj is None:
            return self
        return getattr(obj, self.priv, None)

    def __set__(self, obj, value):
        hints = get_type_hints(type(obj), include_extras=True)
        ann   = hints.get(self.pub)
        if ann and hasattr(ann, "__metadata__"):
            for constraint in ann.__metadata__:
                if callable(constraint):
                    if not constraint(value):
                        raise ValueError(f"{self.pub}={value!r} fails constraint")
        setattr(obj, self.priv, value)


def positive(x) -> bool:
    return isinstance(x, (int, float)) and x > 0

def short_str(x) -> bool:
    return isinstance(x, str) and len(x) <= 20


class Sensor:
    reading: Annotated[float, positive] = _Constrained()   # type: ignore[assignment]
    label:   Annotated[str,   short_str] = _Constrained()  # type: ignore[assignment]

    def __init__(self, label: str, reading: float):
        self.label   = label
        self.reading = reading

    def __repr__(self):
        return f"Sensor({self.label!r}, {self.reading})"


# ── NamedTuple ────────────────────────────────────────────────────────────────

class Span(NamedTuple):
    start: int
    end:   int
    label: str = ""

    def length(self) -> int:
        return self.end - self.start

    def overlap(self, other: Span) -> int:
        return max(0, min(self.end, other.end) - max(self.start, other.start))


# ── numbers ABC ──────────────────────────────────────────────────────────────

class Rational(numbers.Rational):
    """Minimal rational backed by integer numerator/denominator."""

    def __init__(self, num: int, den: int = 1):
        if den == 0:
            raise ZeroDivisionError
        g = _gcd(abs(num), abs(den))
        sign = -1 if den < 0 else 1
        self._n = sign * num // g
        self._d = sign * den // g

    # numbers.Rational interface
    @property
    def numerator(self) -> int:   return self._n
    @property
