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
import types
from collections.abc import Mapping, Sequence, MutableMapping, MutableSequence, Iterable, Iterator, Callable, Hashable, Generic, Sized, Set, Tuple, AnyStr
from functools import partial
from operator import attrgetter
from pprint import pformat
from re import compile as compile_re
from re import sub as sub_re
from shutil import rmtree
from sys import platform
from threading import Lock
from types import FunctionType, BuiltinFunctionType, MethodType, CodeType, FrameType, TracebackType, ModuleType, SliceType, UnionType, NoneType, EllipsisType, ClassMethodDescriptorType, AsyncGeneratorType, GeneratorType, IterableType, IntEnum, EnumMeta, BaseExceptionGroup, ExceptionGroup, BaseException, IOError, OSError, OSErrorBase, SyntaxError, IndentationError, EOFError, StopIteration, AttributeError, ImportError, IndexError, KeyError, LookupError, MemoryError, NameError, OverflowError, ReferenceError, RuntimeError, RecursionError, RuntimeErrorBase, StopAsyncIteration, TypeError, UnboundLocalError, ValueError, ZeroDivisionError, AssertionError, BufferError, FloatingPointError, GeneratorExit, ImportWarning, ImportWarningBase, ReferenceWarning, ResourceWarning, SecurityWarning, DeprecationWarning, FutureWarning, PendingDeprecationWarning, RuntimeWarning, SyntaxWarning, UnicodeWarning, UserWarning, Warning, WarningBase, WarningMessage, WarningModifiers, WarningCategoryFilter, WarningMessageFilters, WarningMessageModifier, WarningCategory, WarningCategories, WarningCategoryFilterSet, WarningCategoryFilterTuple, WarningCategoryFilterList, WarningCategoryFilterDictionary, WarningCategoryFilterObject, WarningCategoryFilterClass, WarningCategoryFilterModule, WarningCategoryFilterPackage, WarningCategoryFilterRoot, WarningCategoryFilterNone, WarningCategoryFilterAll, WarningCategoryFilterEmpty, WarningCategoryFilterTrue, WarningCategoryFilterFalse, WarningCategoryFilterNot, WarningCategoryFilterAnd, WarningCategoryFilterOr, WarningCategoryFilterXor, WarningCategoryFilterNegate, WarningCategoryFilterInvert, WarningCategoryFilterBitwiseAND, WarningCategoryFilterBitwiseOR, WarningCategoryFilterBitwiseXOR, WarningCategoryFilterBitwiseNOT, WarningCategoryFilterBitwiseINVERT, WarningCategoryFilterBitwiseAND2, WarningCategoryFilterBitwiseOR2, WarningCategoryFilterBitwiseXOR2, WarningCategoryFilterBitwiseNOT2, WarningCategoryFilterBitwiseINVERT2, WarningCategoryFilterBitwiseAND3, WarningCategoryFilterBitwiseOR3, WarningCategory