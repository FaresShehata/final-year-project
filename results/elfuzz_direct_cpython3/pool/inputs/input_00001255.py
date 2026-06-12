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
import time
from collections import Counter, defaultdict, deque
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    ClassVar,
    Generic,
    Iterator,
    Literal,
    Protocol,
    TypeVar,
    overload,
    runtime_checkable,
)
from unittest.mock import Mock, patch

import pytest
from pydantic import BaseModel, ValidationError


@dataclasses.dataclass(frozen=True)
class Foo:
    bar: str = "Bar"


def test_data_classes():
    assert repr(Foo()) == 'Foo(bar="Bar")'


# @pytest.mark.skip(reason='Not ready yet')
@pytest.mark.parametrize(
    ["name", "expected"],
    [
        ("foo", {"type": "value", "value": "foo"}),
        (1.5, {"type": "number", "number": 1.5}),
        ([], {"type": "list", "list": []}),
        ({"a": 1}, {"type": "object", "object": {"a": 1}}),
        (("abc"), {"type": "string", "string": '"abc"'}),
        ((b'xyz'), {'type': 'binary', 'bytes': b'xyz'}),
        (Foo(), {'type': 'object', 'object': {'bar': 'Bar'}}),
    ],
)
async def test_json(name, expected):
    name_bytes = bytes(str(name), encoding="utf-8")
    encoded_name = json.dumps(name).encode("ascii")

    with patch.object(json.encoder, "iterencode", return_value=[encoded_name]) as iter_encode_mock:
        result = await json.dumps(name)

    assert result == expected
    assert iter_encode_mock.call_args.args[0] == [
        name,
        None,
    ]


# @pytest.mark.skip(reason='Not ready yet')
async def test_json_errors():
    with pytest.raises(TypeError):
        await json.dumps(3)


async def _json_getter(obj):
    if isinstance(obj, int):
        return obj + 1
    elif isinstance(obj, str):
        return obj * 2
    else:
        raise TypeError()


async def test_json_dotted_path():
    names = ["foo", "456"]
    numbers = [3, 7]
    mixed = zip(names, numbers)
    encoded_names_and_numbers = list(map(_json_getter, mixed))

    encoded_names_and_numbers_str = json.dumps(encoded_names_and_numbers)
    decoded_names_and_numbers = json.loads(encoded_names_and_numbers_str)

    assert len(decoded_names_and_numbers) == 2
    assert (names[0], numbers[0]) in decoded_names_and_numbers
    assert (names[1], numbers[1])