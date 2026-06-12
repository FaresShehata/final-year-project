"""
Seed 05 — Concurrency (threading/multiprocessing/concurrent.futures),
          string parsing (ast.literal_eval, tokenize, textwrap, string.Formatter),
          typing extras (TypedDict, ParamSpec, Concatenate, TypeAlias, Never,
          Annotated, get_type_hints, reveal_type stub),
          __class_getitem__, __set_name__, __init_subclass__,
          contextlib (suppress, redirect_stdout, AbstractContextManager),
          numbers ABC, pathlib, tempfile, csv, base64, hashlib, hmac, secrets
"""

from __future__ import annotations

import ast
import base64
import binascii
import csv
import hashlib
import hmac
import io
import itertools
import multiprocessing
import numbers
import os
import pathlib
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
    Annotated,
    Any,
    Callable,
    ClassVar,
    Final,
    Generic,
    Literal,
    NamedTuple,
    Never,
    ParamSpec,
    TypeAlias,
    TypedDict,
    TypeVar,
    get_type_hints,
)

T  = TypeVar("T")
P  = ParamSpec("P")

# ── TypeAlias ────────────────────────────────────────────────────────────────

JsonValue: TypeAlias = "int | float | str | bool | None | list[JsonValue] | dict[str, JsonValue]"
JsonStr: TypeAlias = str
JsonStrs: TypeAlias = list[JsonStr]
IntOrStr: TypeAlias = "int | str"
JsonStrToJsObj: TypeAlias = Callable[[JsonStr], Any]

# ── TypedDict ────────────────────────────────────────────────────────────────

# https://peps.python.org/pep-0589/
# https://www.python.org/dev/peps/pep-0483/

class JsObject(TypedDict):
	/**
	 * The name of the object.
	 */
	name: str
	
	/**
	 * The age of the person.
	 */
	age: int
	
	/**
	 * Whether or not the person is a student.
	 */
	is_student: bool
"""

JsArray: TypeAlias = List[JsObject]

js_obj_str: JsonStr = """
{
	"name": "Alice",
	"age": 20,
	"is_student": true
}"""


def js_array_to_js_obj(
	js_object_json_str_list: List[JsonStr],
) -> List[JsObject]:
	return [
		json.loads(json_str)
		for json_str in js_object_json_str_list
	]


# ── ParamSpec ────────────────────────────────────────────────────────────────

paramspec_example_1: P
paramspec_example_2: P
paramspec_example_3: P

# ── TypedDict ────────────────────────────────────────────────────────────────

class MyDict(TypedDict):
	a: int
	b: str


def typed_dict_paramsexample(
	dict_param: MyDict[P, T],
	list_param: List[T],
	int_param: int,
	str_param: str,
	func_param: Callable[P, T],
	tuple_param: Tuple[int, str],
	set_param: Set[int],
	frozenset_param: FrozenSet[int],
	dict_param_2: Dict[str, int],
	mydict_param: MyDict[P, T],
) -> None:
	pass


# ── Annotated ────────────────────────────────────────────────────────────────

AnnotatedGood: Annotated[int, "This is good."]
AnnotatedBad: Annotated[float, "This is bad."] = 1.0


# ── ClassVar ────────────────────────────────────────────────────────────────

class MyClass:
	_class_var: ClassVar[int] = 0

instance_var: int = 0

a: ClassVar[int] = 0
b: ClassVar[int]

c: int = 0
d: int

e: ClassVar[int] = 0
f: ClassVar[int]

g: ClassVar[int] = 0
h: ClassVar[int]

i: int = 0
j: int

k: ClassVar[int] = 0
l: ClassVar[int]

m: int = 0
n: int

o: ClassVar[int] = 0
p: ClassVar[int]