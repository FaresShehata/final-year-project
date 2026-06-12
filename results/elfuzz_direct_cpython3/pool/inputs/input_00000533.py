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
import re
import signal
import sys
import time
import threading as pyth_tread
import tokenize as python_tokenize
import types
import unittest.mock
import uuid
import weakref
from abc import abstractmethod
from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from contextlib import suppress, redirect_stdout, AbstractContextManager
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal
from functools import partial, singledispatch
from glob import glob
from inspect import getmembers, signature, Parameter, isroutine, unwrap, cleandoc
from itertools import count, cycle
from operator import attrgetter
from pathlib import Path
from pickle import loads, dumps
from pprint import PrettyPrinter
from random import randrange, sample, choice
from reprlib import recursive_repr
from re import escape
from re import Pattern as re_Pattern
from re import search, match, findall, sub, split
from re import IGNORECASE as RE_FLAG_IGNORECASE
from re import DOTALL as RE_FLAG_DOTALL
from re import MULTILINE as RE_FLAG_MULTILINE
from re import VERBOSE as RE_FLAG_VERBOSE
from shutil import disk_usage, rmtree, which
from subprocess import run, PIPE
from statistics import mean, median, stdev
from string import Template, Formatter, ascii_letters, punctuations
from string import ascii_lowercase, digits, hexdigits
from struct import pack
from sys import intern
from sys import argv as sys_argv
from sys import maxsize as sys_maxsize
from sys import path as sys_path
from tempfile import TemporaryDirectory as TempDir
from tempfile import NamedTemporaryFile as NTempFile
from textwrap import dedent
from textwrap import indent
from textwrap import fill
from textwrap import wrap
from textwrap import TextWrapper
from textwrap import wrap as textwrap_wrap
from textwrap import shorten
from textwrap import TextWrapper as TextWrapper_TextWrapper
from textwrap import dedent as textwrap_dedent
from textwrap import indent as textwrap_indent
from textwrap import fill as textwrap_fill
from thread import allocate_lock, LockType
from traceback import format_exception as trace_format_exc
from traceback import extract_stack as trace_extract_stack
from traceback import format_tb as trace_format_tb
from traceback import print_exception as trace_print_exc
from traceback import print_list as trace_print_list
from traceback import print_stack as trace_print_stack
from traceback import print_tb as trace_print_tb
from typing import Any, Callable, ClassVar, Counter, Dict, FrozenSet, \
    Generator, Generic, Iterable, Iterator, List, Literal, Mapping, Match, \
    MutableMapping, NewType, Optional, Pattern, Set, Tuple, Type, TypeVar, \
    Union, overload, no_type_check, runtime_checkable, Protocol
from types import ModuleType, TracebackType
from types import FunctionType as PythonFunctionType
from types import MethodDescriptorType
from typing import _eval_type, _type_var_cache
from typing_extensions import TypedDict, ParamSpec, Concatenate, \
    TypeAlias, Never, Annotated, get_type_hints, reveal_type, \
    get_origin, get_args, get_type_hints
from typing import get_annotations as type_hints
from typing import get_origin as typetyp_get_origin
from typing import get_args as typetyp_get_args
from typing import get_type_hints as typetyp_get_type_hints
from typing import get_args as typetyp_get_args
from typing import get_origin as typetyp_get_origin
from typing import get_type_hints as typetyp_get_type_hints
from typing import get_validators as typetyp_get_validators
from typing import get_type_hints as typetyp


dis.disassemble(codeobj)

from dis import dis as disassemble_py
disassemble_py(codeobj)