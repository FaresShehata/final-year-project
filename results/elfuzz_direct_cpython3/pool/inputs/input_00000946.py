"""
Seed 05 — Concurrency (threading/multiprocessing/concurrent.futures),
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import OrderedDict, Counter
from collections.abc import Mapping, MutableMapping, MutableSet, MutableSequence
from dataclasses import dataclass, field, InitVar
from functools import wraps
from inspect import signature
from itertools import product, chain, combinations_with_replacement, product
from logging import Logger
from multiprocessing.pool import Pool
from os.path import basename, splitext
from pathlib import Path
from re import compile, Pattern, MULTILINE, IGNORECASE, VERBOSE
from shutil import copyfileobj, move, rmtree, which
from subprocess import PIPE, STDOUT, Popen, run as pypopen
from textwrap import shorten
from tempfile import TemporaryDirectory
from timeit import default_timer as timer
from uuid import UUID, uuid1, uuid4
from warnings import warn

from bs4 import BeautifulSoup
from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.name import Name
from jinja2.ext import Extension
from lxml.etree import ElementTree, XMLParser, fromstring
from packaging.version import Version
from pkg_resources import DistributionNotFound, WorkingSet, resource_filename
from pydantic import PrivateAttr
from pydantic.typing import Literal, LiteralString
from schema import Schema, And, Or, Use, SchemaError, Regex, Optional as SCHEMAOptional, SchemaMetaClass
from tabulate import tabulate
from termcolor import colored
from tqdm.auto import tqdm

from .._version import __version__
from ..utils import (
    is_ascii,
    is_binary_string,
    is_byte_string,
    is_cjk,
    is_date_time_str,
    is_decimal,
    is_email_address,
    is_file_path,
    is_float,
    is_hostname,
    is_int,
    is_ip_address,
    is_json_serializable,
    is_multibyte_string,
    is_octal,
    is_password,
    is_phone_number,
    is_port_number,
    is_punycode,
    is_quoted_string,
    is_safe_uri,
    is_search_engine_url,
    is_semver_version,
    is_short_unicode_word,
    is_titlecase_word,
    is_traditional_chinese,
    is_unsafe_uri,
    is_unicode_word,
    is_valid_ipv6_address,
    is_uuid,
    is_xml,
       Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)
from typing_extensions import (
    TypedDict,
    ParamSpec,
    Concatenate,
    TypeAlias,
    Never,
    Annotated,
    get_args,
    get_origin,
)

import concurrent.futures
import ipaddress
import openssl.crypto
import pytz
import requests
import spacy
import validators
from contextlib import redirect_stderr, redirect_stdout
from dateutil.tz import tzlocal, tzutc
from datetime import timedelta, timezone
from email.parser import BytesParser
from email.utils import formataddr, parseaddr, parsedate_tz
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from loguru import logger
from openpyxl import Workbook
from pydantic import BaseModel, root_validator, validator
from safetensors.numpy import load as load_safetensor
from sqlalchemy.orm.session import Session

from .config import Config
from .exceptions import (
    APIError,
    InvalidArgumentTypeError,
    InvalidDataFormatError,
    InvalidDatetimeValueError,
    InvalidEmailValueError,
    InvalidFieldLengthError,
    InvalidFieldValueError,
    InvalidPasswordValueError,
    InvalidPhoneNumberValueError,
    InvalidRangeValueError,
    InvalidRegexPatternError,
    MismatchedMappingKeysError,
    MismatchedSequenceElementsError,
    MismatchedTupleValuesError,
    MissingRequiredArgumentsError,
    UnknownAttributeError,
)
from .typing_ext import (
    AwaitableType,
    AnyCallable,
    AsyncIterableType,
    CoroutineType,
    DeferredType,
    FirstArgType,
    FirstReturnType,
    LambdaReturnType,
    LazyType,
    SecondArgType,
    ThirdArgType,
    ThreadingExecutorType,
    ThreadPoolExecutorType,
    WrappedFunctionType,
)


# @classmethod decorator
def classmethod_decorator(func: Callable = None, *, name: