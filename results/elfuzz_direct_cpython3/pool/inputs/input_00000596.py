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
import os
import re
import secrets
import shutil
import sys
import tempfile
import threading
import tokenize
import types
import time
import traceback
import urllib.parse as urlparse
import uuid
import warnings
from abc import abstractmethod, ABCMeta
from collections.abc import Iterable, Iterator, Sequence, Callable
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from functools import partial, wraps, lru_cache, singledispatchmethod
from inspect import signature, Parameter, isawaitable, AsyncGenerator, iscoroutinefunction
from io import TextIOWrapper
from itertools import chain
from logging import getLogger, CRITICAL, WARNING, ERROR
from operator import itemgetter
from pprint import pformat
from random import choice, randint
from re import Pattern
from tempfile import NamedTemporaryFile, TemporaryDirectory
from time import sleep
from typing import (
    Any,
    overload,
    Awaitable,
    NoReturn,
    Optional,
    Union,
    Tuple,
    List,
    Dict,
    Generator,
    Deque,
    Set,
    FrozenSet,
    ClassVar,
    Mapping,
    Counter,
    Generic,
    Protocol,
)
from typing_extensions import Literal, TypedDict, ParamSpec, Concatenate, TypeAlias, Never, Annotated, get_args, get_origin, _AnnotatedAlias
from types import CodeType, FunctionType, BuiltinFunctionType, MethodType, ModuleType
from weakref import WeakValueDictionary, ref
from zlib import crc32

from .base import BaseObject, ObjectMap, ObjectArray, ObjectSeq, ObjectTuple, ObjectSet, ObjectFrozenSet, ObjectEnum, ObjectList, ObjectDeque, ObjectCounter, ValueTypes
from ..utils.misc import *
from ..utils.collection import Queue, PriorityQueue
from ..utils.type_utils import resolve_annotated_typename, Falsy, NonStringLiteral, is_iterable, is_number, is_integer, is_float, is_bool, is_string, is_bytes, is_text, is_mapping, is_sequence, is_set, is_frozen_set, is_none, is_str_like, is_dict_like, is_list_like, is_tuple_like, is_deque_like, is_counter_like, is_generator, is_async_generator, is_coroutine_function, is_coroutine_callable, is_method, is_property, is_abstract_base_class, is_generic, is_protocol, is_dataclass, is_union, is_optional, is_literal, is_enum, is_module, is_built_in_module, is_builtin_function_or_method, is_closure, is_magic_method, is_magic_attribute, is_operator_method, is_unary_operator_method, is_binary_operator_method, is_trinary_operator_method, is_postfix_operator_method, is_lshift_operator_method, is_rshift_operator_method, is_bitwise_and_operator_method, is_bitwise_xor_operator_method, is_bitwise_or_operator_method, is_power_operator_method, is_modulo_operator_method, is_division_operator_method, is_floor_division_operator_method, is_true_division_operator_method, is_integer_division_operator_method, is_exponentiation_operator_method, is_left_shift_operator_method, is_right_shift_operator_method, is_bitwise_and_operator_method, is_bitwise_xor_operator_method, is_bitwise_or_operator_method, is_power_operator_method, is_modulo_operator_method, is_division_operator_method, is_floor_division_operator_method, is_true_division_operator_method, is_integer_division_operator_method, is_classmethod, is_staticmethod, is_metaclass, is_new_style_class, is_weakref_proxy, is_weakref_object, is_weakref_value, is_weakref_instance, is_weakref_weakly_referenced, is_weakref_referrers, is_weakref_reachable, is_weakref_directly_referenced_by, is_weakref_indirectly_referenced_by, is_weakref_not_referenced_by, is_weakref_alive, is_weakref_dead, is_weakref_alive_or_dead, is_weakref_alive_or_dead_or_unknown, is_weakref_alive_or_dead_or_unknown_or_live, is_weakref_alive_or_dead_or_unknown_or_live_or_dead, is_weakref_alive_or_dead_or_unknown_or_live_or_dead_or_unknown, is_weakref_alive_or_dead_or_unknown_or_live_or_dead_or_unknown_or_live_or_dead, is