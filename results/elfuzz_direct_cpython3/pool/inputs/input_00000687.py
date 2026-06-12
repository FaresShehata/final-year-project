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
    """Demo of basic usage of threading.Thread."""
    def thread_function(name):
        print(f"Thread {name}: starting")
        # sleep(2)
        print(f"Thread {name}: finishing")

    with ThreadPoolExecutor(max_workers=3) as executor:
        for i in range(3):
            t