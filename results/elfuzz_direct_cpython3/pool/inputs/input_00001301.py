"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import bisect
import dataclasses
import enum
import heapq
import json
import random
import re
import sys
import time
import traceback
from collections.abc import Callable, Iterable, Iterator, Mapping, MutableMapping, Sequence, Set, Sized
from contextlib import suppress
from datetime import timedelta
from functools import partial
from itertools import chain, islice
from logging import DEBUG, INFO, WARNING
from numbers import Integral
from pathlib import Path
from types import GenericAlias, NoneType, TracebackType
from typing import Any, ClassVar, Literal, TypedDict, TypeGuard, TypeVar, Union, cast
from warnings import warn


class BoringException(Exception):
    pass


def dummy():
    """This function is used to make the example more readable."""
    return "dummy"


def run():
    """main entry point"""
    print("##############################")
    print("#         Seed 02            #")
    print("##############################\n")

    print("asyncio")
    a = asyncio.run(asyncio.sleep(1))
    assert a == 1.0

    print("\ndataclasses")
    @dataclasses.dataclass()
    class Point:
        x: int
        y: int
        z: int | None = None

    p = Point(x=2, y=4)
    print(p)  # -> Point(x=2, y=4, z=None)

    @dataclasses.dataclass(order=True)
    class Person:
        name: str
        age: int

    person1 = Person('John', 25)
    person2 = Person('Alice', 30)
    person3 = Person('Bob', 28)

    print(person1 < person2)  # -> True

    person_dict = {'name': 'John', 'age': 25}
    person = Person(**person_dict)
    print(person.name)  # -> John

    print('\nprotocols')
    if isinstance(None, Enum):  # type: ignore
        raise TypeError('None cannot be an instance of enum.Enum')

    @enum.unique
    class Suit(enum.Enum):
        HEARTS = '\N{BLACK HEART SUIT}'
        DIAMONDS = '\N{BLACK DIAMOND SUIT}'

    suit = Suit.HEARTS
    print(suit.value)  # -> ♥

    print('\ndataclasses.__slots__')
    @dataclasses.dataclass(slots=True)
    class Vector2D:
        x: float
        y: float

    v = Vector2D(1.0, 1.0)
    try:
        v.z = 1.0
    except AttributeError as err:
        print(err.__cause__)  # -> '_SlotAssignmentError'
        print(err.args[0])  # -> 'Vector2D' object has no attribute '__dict__'

    print('\ndataclasses.__annotations__ and type hints')
    @dataclasses.dataclass(init=False, kw_only=True, slots=True)
    class Book:
        title: str
        author: str
        price: float
        pages: int

    book1 = Book(title='The Great Gatsby', author="F. Scott Fitzgerald", price=12.99, pages=218)
    print(book1.price)  # -> 12.99

    print('\ndataclasses._field_flags')
    @dataclasses.dataclass(frozen=True)
    class User:
        id: int
        username: str

    user = User(id=1, username='john_doe')
    try:
        user.id = 2
    except AttributeError as err:
        print(err.__cause__)

    print('\nstructural pattern matching')
    movie = {
        'title': 'Inception',
        'rating': 5.1,
        'year': 2010,
    }

<|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|>    print(movie.rating)  # -> 5.1

    print('\ntype aliases')
    T = TypeVar('T')


    def normalize(value: T, minimum: T, maximum: T) -> T:
        delta = (maximum - minimum)
        if delta == 0:
            raise ValueError(f"Minimum ({minimum}) must not be equal to maximum ({maximum})")
        normalized_value = ((value - minimum) / delta * 100)
    shapes = [Circle(radius=2), Square(side_length=3)]
    for shape in shapes:
        match shape:
            case Square(side_length=sq_side):
                print(f"A square with side length {sq_side}")
            case Circle(radius=c_radius):
                print(f"A circle with radius {c_radius}")

   