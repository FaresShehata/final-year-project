"""
Seed 01 — OOP, metaclasses, descriptors, decorators, context managers, generators
"""

from __future__ import annotations

import abc
import contextlib
import functools
import inspect
import itertools
import operator
import os
import pathlib
import pickle
import random
import re
import string
import typing as t
import weakref
from collections.abc import (
    Awaitable,
    Callable,
    Collection,
    Iterable,
    Iterator,
    Mapping,
    Sequence,
    Set,
    MutableMapping,
)
from dataclasses import dataclass, field, KW_ONLY
from datetime import datetime, timedelta
from enum import Enum, auto, unique
from enum import (
    IntEnum,
    IntFlag,
    IntDescriptionMixin,
    StrEnum,
    ReprEnum,
    IntFlags,
)
from enum_tools import EnumMeta
from enum_tools.enum_tools import EnumToolsMeta
from enum_tools.repr_enum import ReprEnumMeta


def _get_json_encoder_class() -> type[json.JSONEncoder]:
    """Get the JSON encoder class."""
    try:
        from json.encoder import JSONEncoder

        return JSONEncoder
    except ImportError:
        pass

    try:
        from jsonlib.jsonencoder import JSONEncoder

        return JSONEncoder
    except ImportError:
        pass

    raise RuntimeError("No JSON encoder found.")


JSONEncoderType = t.TypeVar("JSONEncoderType", bound=type[_get_json_encoder_class()])


def get_json_encoder() -> JSONEncoderType:
    """Get a serializable JSON encoder for all classes in this module."""
    return _get_json_encoder_class()


@t.overload
def is_iter(obj: None | Collection[t.Any]) -> bool: ...: ...
@t.overload
def is_iter(obj: None | Iterable[t.Any]) -> bool: ...
@t.overload
def is_iter(obj: None | Iterator[t.Any]) -> bool: ...


def is_iter(
    obj: None | Collection[t.Any]
    | Iterable[t.Any]
    | Iterator[t.Any],
) -> bool:
    """Check whether an object is iterable.

    >>> is_iter(None)
    True

    >>> is_iter([])
    True

    >>> is_iter(range(3))
    True

    >>> is_iter(iter([]))
    True

    >>> is_iter('foo')
    True

    >>> is_iter({1, 2})
    True

    >>> is_iter((1,))
    True

    >>> is_iter((1, 2))
    True

    """
    return isinstance(obj, (Collection, Iterable, Iterator))


def is_dict(obj: None | dict[t.Any, t.Any]) -> bool:
    """Check whether an object is a dictionary.
    
    Note that this function considers ``OrderedDict`` to be a dictionary.
    
    >>> is_dict({})
    True
    
    >>> is_dict(dict())
    True
    
    >>> is_dict(OrderedDict())
    True
    
    >>> is_dict(set())
    False
    
    """
    return isinstance(obj, dict)


def is_list(obj: None | list[t.Any]) -> bool:
    """Check whether an object is a list.
    
    >>> is_list([])
    True
    
    >>> is_list([1])
    True
    
    >>> is_list(tuple())
    False
    
    """
    return isinstance(obj, list)


def is_type(obj: None | type[Any]) -> bool:
    """Check whether an object is a type.
    
    This includes built-in types like ``int``, but does not include user-defined classes.
    
    >>> is_type(type)
    True
    
    >>> is_type(int)
    False
    
    """
    return isinstance(obj, type)
    

def iter_dfs(obj: ObjectClassRef | ObjectClassType | None) -> Generator[type, None, None]:
    """Iterate over a class and its descendants using depth-first search.

    Args:
        obj: The starting class or descriptor.

    Yields:
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


def iter_dfs_up(obj: ObjectClassRef | ObjectClassType | None) -> Generator[type, None, None]:
    """Iterate over a class's ancestors in reverse order by depth-first search.

    Args:
        obj: The starting class or descriptor.

    Yields:
        A descriptor of each class in the hierarchy, right-to-left.

    Examples:
        >>> class Base1: ...
        >>> class Base2: ...
        >>> class Sub(Base1): ...
        >>> class SubSub(Sub, Base2): ...
        >>> class SubSubSub(SubSub): ...
        
        >>> list(iter_dfs_up(Base1)) == [Base1, Sub, SubSub, SubSubSub, Base2]
        True
        
        >>> list(iter_dfs_up(SubSubSub)) == [Base2, SubSub, Sub, Base1, Base2]
        True
    
    """
    if obj is None:
        yield from ()
    elif is_descriptor(obj):
        yield obj.__origin__
        yield obj.__member__
    else:
        yield obj
        for superclass in obj.__mro__[1:]:
            yield from iter_dfs_up(superclass)


def iter_fields(cls: Type) -> Iterator[tuple[str, Field]]:
    """Iterate over a class' fields.

    Args:
        cls: The class whose fields are being enumerated.

    Yields