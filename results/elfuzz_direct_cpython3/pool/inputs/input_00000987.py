"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import bisect
import dataclasses
import enum
import functools as ft
from collections.abc import Iterable, Iterator, Sequence
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Callable, Generic, Literal, Optional, TypeVar, cast

T = TypeVar("T")
U = TypeVar("U")


class AsyncEnum(enum.Enum):
    """Custom class that implements awaitable members"""

    @classmethod
    def _missing_(cls: type[AsyncEnum], value: object) -> AsyncEnum:
        match cls.__members__.get(value):
            case None | cls.FALLTHROUGH:
                raise ValueError(f"Invalid {cls.__qualname__}: {value!r}")
            case member if not isinstance(member.value, Awaitable):
                return member
            case member if callable(member.value):
                try:
                    return AsyncEnum._new(cls, member.name, await member.value())
                except TypeError:
                    # The awaited object does not accept the "()" call.
                    # We look for a method with the name "__call__".
                    # If it exists, we use it to initialize an instance of this enum.
                    method_name = "__call__"
                    if hasattr(member.value, method_name):
                        argspec = inspect.getfullargspec(
                            getattr(member.value, method_name)
                        )
                        if argspec.varargs is not None or argspec.varkw is not None:
                            raise TypeError(
                                f"{member.value!r} cannot be called with varargs "
                                f"(it has {method_name}() signature)"
                            )

                        # Delete function default values so they don't get passed along to the new instance.
                        del kwargs[arg[0] for arg in argspec.args]
                        return AsyncEnum._new(cls, member.name, member.value(*args, **kwargs))
                    else:
                        raise TypeError(
                            f"{member.value!r} cannot be called (does not have a '__call__' method)"
                        )
                except Exception as e:
                    raise TypeError from e
            case member if isinstance(member.value, Awaitable):
                return member


@dataclasses.dataclass(slots=True)
class Structured:
    """
    Contains arbitrary data.

    This class uses slots, which are faster than normal dictionaries.
    """

    __slots__: tuple[str, ...]


@ft.overload
def make_counter(init_value: int) -> Counter[int]:
    ...


@ft.overload
def make_counter(init_value: str) -> Counter[str]:
    ...


@ft.overload
def make_counter(init_value: float) -> Counter[float]:
    ...


@ft.overload
def make_counter(init_value: bool) -> Counter[Any]:
    ...


@ft.overload
def make_counter(init_value: None) -> Counter[None]:
    ...


@ft.overload
def make_counter(init_value: dict[int, str]) -> Counter[tuple[int, str]]:
    ...


def make_counter(init_value: Any) -> Counter[Any]:
    """Create an empty counter initialized by the given value."""
    match init_value:
        case None | bool():
            return Counter({})
        case int():
            return Counter({i: chr(i + ord("A")) for i in range(init_value)})
        case str():
            return Counter({s.upper(): s for s in init_value})
        case float():
            return Counter({Decimal(s): s for s in init_value.split()})
        case dict():
            return Counter(dict((k, v) for k, v in sorted(init_value.items())))
    overload,
)
from typing_extensions import (
    Concatenate,
    ParamSpec,
    TypeGuard,
    Unpack,
    NoTypingInfo,
)

__all__ = [
    "any",
    "all",
    "any_iterable",
    "async_all",
    "async_any",
    "avg",
    "bimap",
    "by_key",
    "combine",
    "compare_operators",
    "counter",
    "defaultdict",
    "deepcopy",
    "divide_by_zero",
    "enum_count",
    "enumerate",
    "exception_group",
    "filter_keys",
    "float_range",
    "format_time",
    "freeze_dict",
    "flat_map",
    "func_args",
    "gcd",
    "hasattr_or_none",
    "hashable",
    "identity",
    "indexed_combination",
    "index_of_first_true",
    "isinstance_or_subclass",
    "iterkeys",
    "isinstance_or_subclass_tuple",
    "len_sorted",
    "listify",
    "max_increasing_subsequence",
    "min_max",
    "next",
    "next_with_default",
    "norm",
    "ordered",
    "partition",
    "pop_last",
    "pop_safely",
    "promote",
    "range2",
    "reversed_justified",
    "round_half_up",
    "seq_contains",
    "seq_make_from_lists",
    "slice_eq",
    "sorted_unique",
    "sort_uniquely",
    "sum",
    "swap_values",
    "table",
    "tuple_addition",
    "tuple_multiply",
    "unzip3",
    "valmap",
    "values_of",
    "with_metaclass",
    "year_month_day",
]

P = ParamSpec("P")
R = TypeVar("R")


def any(*values: Any) -> bool:
    """
    Return True if any of the values evaluate to true.

    >>> any(1, "", False)
    True
    """
    return any(values)


def all(values: Iterable[Any]) -> bool:
    """
    Return True if all of the values evaluate to true.

    >>> all([True, False])
    False
    """
    return all(values)


def any_iterable(iterable: Iterable[Any]) -> bool:
    """
    Return whether there's at least one iterable item inside the given `iterable`.

    >>> any_iterable([[1]])
    True
    >>> any_iterable([])
    False
    """
    return any(isinstance(item, Iterable) and item for item in iterable)


async def async_all(async_iterable: AsyncIterable[T]) -> bool:
               fn = getattr(obj(), "__init__", None)

        elif inspect.isfunction(obj):
            fn = obj
        else:
            raise TypeError(type(obj))

        # print(fn.__code__.co_code)
        dis.dis(fn)
    except AttributeError:
        print(f"No bytecodes found for {type(obj)}")

print("\nDisassembling bytecodes:")
disassemble_bytecodes(print)
disassemble_bytecodes(range)
disassemble_bytecodes(lambda x: x + 2)

# ── Code objects ──────────────────────────────────────────────────────────────


def show_code_object(code):
    """
    Show the `code` dictionary.

    :param code: The `code` dict from which to display contents.
    """
    print(textwrap.indent(
        f"""\
{code["argcount"]} arguments, {code["posonlyargcount"]} positional-only args, {code["kwonlyargcount"]} keyword only args,\
 {code["locals"]}, flags={hex(code["flags"])}, firstlineno={code["firstlineno"]},
 name="{code['co_name']}",
 argnames=({", ".join(f'"{i}"' for i in code["co_varnames"][:code["argcount"]] if i != "_")}),
 posargs=({", ".join(f'"{i}"' for i in code["co_varnames"][code["argcount"]:code["argcount"]+code["posonlyargcount"]] if i != "_