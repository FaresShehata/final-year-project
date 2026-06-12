"""
Seed 04 — Low-level Python: bytecode introspection, dis, code objects, ctypes,
          struct, array, memoryview, pickle, copyreg, marshal, importlib,
          sys internals, frame inspection, gc, tracemalloc, weakref, __slots__
"""

from __future__ import annotations

import array
import ctypes
import dis
import gc
import importlib
import importlib.abc
import importlib.machinery
import importlib.util
import inspect
import io
import itertools
import os
import pickle
import pprint
import random
import re
import sys
import traceback
import types
import typing
import unittest.mock
import weakref
import weakref.reaction
import weakref.finalizer
import weakref.ref

import contextlib
from collections import (
	ChainMap,
	Callable,
	Collection,
	ConcurrentMapping,
	ConcurrentSet,
	DefaultDict,
	DictView,
	FrozenSet,
	MutableSequence,
	List,
	OrderedDict,
	OrderedSet,
	Optional,
	Set,
	Sequence,
	Sized,
	Tuple,
	TypeVar,
)
from dataclasses import (
	dataclass,
	field,
	fields,
	init,
	new_class,
	replace,
)
from enum import Enum, IntEnum
from functools import cached_property, partialmethod, reduce, update_wrapper
from itertools import chain, tee
from math import pi
from types import FunctionType
from typing import Any, Callable, ClassVar, Generic, Iterable, Literal, Mapping, MutableMapping, NamedTuple, NewType, Sequence, TypeAlias, TypedDict, Union, cast, overload
from typing_extensions import (ClassVar, Deque, LiteralString, Protocol, Self, SupportsIndex, TypedDict, Unpack, runtime_checkable)

from pubsub import pub

from bs4.element import Tag
from docopt import docopt
from google.protobuf.json_format import MessageToJson
from lxml.etree import Element, SubElement
from nagini_contracts.contracts import ContractError
from wsgiref.simple_server import make_server

import js2py
import json
import numpy as np
import pandas as pd
import pytest
import requests
import requests_cache
import statistics
import timeit
import urllib.request
import yaml
import zlib
import zstandard

if sys.version_info >= (3, 8):
	from collections import (
		Counter,
		Deque,
	)
else:
	from backports.cached_property import CachedProperty

from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass
from pydantic.fields import ModelField
from pydantic.main import ModelMetaclass
from pydantic.utils import classproperty

from typing_extensions import (
	Concatenate,
	ParamSpec,
	Protocol,
	Self,
	SynthesizedKwargs,
)

from nianet import *

# ── Nyanet ──────────────────────────────────────────────────────────────────


from nianet.nianet import *
from) -> List[JsObject]:
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
	def with_context(self, *, verbose: bool = False) -> Iterator["Person"]:
		if verbose:
			print(f"With Context Manager - {self}")
			
		yield self
	
	p = Person("Smith")
	with p.with_context(verbose=True) as c:
		print(c.surname)

	@Annotated[
		Person, 
		Annotated["verbose", Annotated[bool, True]]
	]
	def annotated_func(person: Person