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

from collections.abc import Generator, Iterable, Mapping, MutableMapping
from dataclasses import is_dataclass
from functools import partial
from inspect import Parameter, signature
from math import ceil
from re import match
from sys import argv, stderr
from types import TracebackType
from typing import (
	AbstractSet,
	BinaryIO,
	Any,
	ClassVar,
	Dict,
	Final,
	Iterator,
	List,
	Optional,
	Set,
	Tuple,
	Type,
	TypeVar,
	Union,
)
from uuid import UUID

from contextvars import ContextVar
from enum import Enum
from pathlib import Path
from pydantic import BaseModel, create_model
from rich.console import Console
from rich.progress import Progress, TaskID
from rich.prompt import Prompt
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from typing_extensions import Self

from seed02 import do_something_in_background
from seed03 import BinaryFileData, FileReadError
from seed07 import PathLike
from seed08 import PathLikeOrString


# ── json ────────────────────────────────────────────────────────────────────


JsonStr: TypeAlias = str | bytes
JsonObj: TypeAlias = dict[str, JsonValue] | list[JsonValue] | JsonValue
JsonValue: TypeAlias = JsonStr | int | float | bool | None
JsonArray: TypeAlias = list[JsonValue]

json_encodeable_types: tuple[type, ...] = (
	bytes,
	int,
	float,
	bool,
	str,
	type(None),
	list,
	tuple,
	dict,
)


def is_json_value(value: Any) -> bool:
	return isinstance(value, json_encodeable_types)


def encode_json(obj: JsonObj) -> JsonArray:
	return [
		encode_json(item)
		for item in obj.values()
	] if isinstance(obj, dict) else obj


def decode_json(obj: JsonValue) -> JsonObj:
	return {
		key: decode_json(item)
		for key, item in obj.items()
	} if isinstance(obj, dict) else obj


def json_encode(obj: JsonValue) -> JsonStr:
	if not is_json_value(obj):
		raise TypeError("Argument must be json value.")
	
	if isinstance(obj, (bytes, bytearray)):
		obj = obj.decode(errors="replace")
	elif isinstance(obj, str):
		obj = obj.replace("\x00", "\uFFFD")
	
	return str(obj)


def json

def js_array_to_js_obj(
	js_object_json_str_list: List[JsonStr],
) -> List[JsObject]:
	return [
		json.loads(json_str)
		for json_str in js_object_json_str_list
	]


# ── ParamSpec ────────────────────────────────────────────────────────────────


def param_spec_demo() -> Tuple[Tuple[int, ...], int]:
	def wrapper(
		*p: int,
		x: int,
		y: int = 10,
		z: Final[int] = 100,
	) -> Tuple[int, ...]:
		pass

	return wrap(*range(10))


def test_param_spec() -> None:
	assert param_spec_demo() == ((10,), 10)


# ── Annotated ────────────────────────────────────────────────────────────────


def annotated_demo() -> None:

	class Person(NamedTuple):
		surname: str
		
	@contextlib.contextmanager
	def person_name(name: Annotated[str, "Surname"]) -> Iterator[str]:
		try:
			yield name
			
		finally:
			print(f"Goodbye {name}")
			
	with person_name("John") as surname:
		print(surname)
		
	assert defanged_demap()


def annotated_demo_2() -> None:
	
	class A:
		pass
	
	class B(A):
		pass
	
	class C(B):
		pass
	
	class D(C):
		pass
	
	print(D.__mro__)
	
	
def test_context_manager():
	pass


# ── get_type_hints ──────────────────────────────────────────────────────────


def get_all_args(func: Callable[P, T]) -> tuple[tuple[str, Parameter], ...]:

	sig: Signature = signature(func)
	params: Sequence[Parameter] = sig.parameters.values()
	
	return tuple((param.name, param) for param in params)


def get_arg_names_and_types(func: Callable[..., T]) -> tuple[str, type]:

	args: tuple[tuple[str, Parameter], ...]
	argnames, argtypes = zip(*get_all_args(func))
	
	return args


def get_decorated_func_info(decorated_function: Callable[..., T]) -> tuple[tuple[str, type], ...]:

	args: tuple[tuple[str, Parameter], ...] = get_arg_names_and_types(decorated_function)
	
	return args


def get_callable_signature(callable: Callable[..., T]) -> Signature:
	signature_: Signature = signature(callable)
	return signature_

#
# @property
# def get_foo(self):
#     pass
# 
# 
# class Foo(BaseModel):
#     foo: int
#     
#     @classmethod
#     def from_bar(cls, bar: Bar) -> Foo:
#         return cls(foo=bar.bar)
# 
# 
# def get_caller_foo_and_bar(cls: Type[Foo], *args, **kwargs) -> tuple[int, Bar]:
# 	caller_foo: int = cls.foo
# 	
# 	bar: Bar = Bar(bar=caller_foo)
# 	
# 	return caller_foo, bar
# 

def get_type_hints_with_annotations(decorated_function: Callable[..., T]) -> dict[str, type]:
	return get_type_hints(decorated_function, include_extras=True)


def get_annotation_for_param(param: Parameter) -> Optional[type]:
	return param.annotation


def get_parameter_types_from_sig(sig: Signature) -> dict[str, type