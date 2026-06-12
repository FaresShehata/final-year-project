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
import csv
import hashlib
import hmac
import io
import os
import re
import secrets
import shutil
import sys
from abc import ABCMeta
from collections.abc import (
    MutableMapping as MutableMappingABC,
    Sequence,
)
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta
from functools import lru_cache, partialmethod, singledispatch
from itertools import zip_longest
from operator import itemgetter
from pathlib import Path
from pprint import pformat
from random import randint
from statistics import mean
from timeit import Timer
from types import FunctionType
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Generic,
    List,
    Literal,
    Mapping,
    NamedTuple,
    Optional,
    Protocol,
    TextIO,
    Tuple,
    TypedDict,
    Union,
    cast,
)
from unittest.mock import Mock
from uuid import UUID

import click
import humanize
import numpy as np
import pandas as pd
import pydantic
import requests
import requests.adapters
import requests.exceptions
import tomlkit
import urllib3.connection
import yaml
from cached_property import cached_property
from contextlib import suppress
from sqlalchemy.sql.schema import Column
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import OperationalError
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from sqlalchemy.future.engine import _engine_from_config
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool
from sqlalchemy.pool.impl import SingletonThreadPool
from sqlalchemy.types import JSON
# from sqlalchemy.dialects.mssql import VARCHAR
from sqlalchemy.dialects.postgresql.psycopg2 import ARRAY
from sqlalchemy.dialects.mysql.pymysql import BIGINT
from sqlalchemy.dialects.sqlite import TEXT, NUMERIC
from sqlalchemy_utils import database_exists
from sqlalchemy_utils.functions import drop_database, create_database, create_tables

from . import common


def seed_01() -> None:
    """
    Seed 01 — Numbers & Strings,
                math operators (power, modulo), int/float/complex conversions,
                range(), reversed(range()), sum(), abs(),
                list(), tuple(), set(), dict(), enumerate()
    """

    print(f'\n{common.BG}SEED 01—Numbers and Strings')

    # Numpy is a large scientific computing library for Python.
    # It provides support for multi-dimensional arrays, matrices, and linear algebra operations.
    # It also includes tools for working with numeric data, plotting data, and performing statistical analysis.

    print('\nNumpy')
    print('=' * len('Numpy'))
    print('About Numpy')
    print('-' * len('About Numpy'))

    print("NumPy is the fundamental package needed for scientific computing with Python.\n"
          "It contains among other things:\n"
          "- a powerful N-dimensional array object,\n"
          "- sophisticated (broadcasting) functions,\n"
          "- tools for integrating C/C++ and Fortran code,\n"
          "- useful linear algebra, Fourier transform, and random number capabilities.")
    print()

    print("- NumPy Array")
    print('An ndarray (short for n-dimensional array) is a grid of values '
          'that can be accessed by using an index expression,\n'
          '(often called a “slice” or an “index sequence”) that specifies\n'
          'one row, one column, or a diagonal of the array.\nThe general form is:')
    print('[row, col, ..., diag]')
    print('The dimensions are specified in square brackets \n'
          'and separated by commas.')

    print("\nndarray.ndim gives us the rank (or dimensionality)\nof an nd-array.")
    print("ndarray.shape returns a tuple containing the size of each dimension.")
    print("ndarray.size = product(shape)")
    print("ndarray.dtype describes the type contained within the nd-array.")

    print('\nCreating an ndarray instance')
    print('=' * len('Creating an ndarray instance'))
    print("We can use several ways to initialize ndarrays:")
    print("[1] Using a nested list:")
    print("(We can also pass in some optional keyword arguments.)")

    print("[2] Using np.array()")
    print('(If we want to specify multiple axes at once.)')

    print("[3] Using np.arange()")
    print('(Similar to range but produces a numpy