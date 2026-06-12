"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import bisection
import collections.abc as cabc
import itertools
import math
import os
import platform
import random
import re
import string
import subprocess
import sys
import threading
import time
import types
import typing as t
import weakref

import numpy as np
import pandas as pd
import pytest
import requests as req
import requests_cache as rcc
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from scipy.stats import norm
from sortedcontainers import SortedSet
from toolz.curried import (
    groupby,
    identity,
    partition_all,
)

import py_entitymatching as em
import py_entitymatching.catalog.catalog_utils as cu
import py_entitymatching.base.constants as const
from py_entitymatching.utils.generic_helper import (
    get_unique_str,
    is_empty_list_or_dict,
    is_instance,
    is_iterable,
)
from py_entitymatching.utils.validation_helper import validate_input_args

import pyomnisci as om


if any([sys.version_info >= (3, 9)] +
       [(platform.system() != "Windows" or platform.release() >= "10")]
      ):
    # Python >= 3.9 and MacOS >= 10.15 don't have the bug where 'float('nan')' can be coerced to an integer.
    # We need this check because older versions of PyPy throw exceptions on the line below.
    # This means we cannot use this code for these platforms in our tests.

    class BaseExceptionGroup(Exception):
        """
        A container for multiple exceptions that were raised during execution
        of a single potentially long-running operation.
        """

        def __init__(
                self,
                excs: Union[
                    tuple[BaseException],
                    Iterable[tuple[BaseException]],
                    Sequence[Union[BaseException, Tuple[BaseException]]],
                ],
                message: str | None = None,
                *,
                context: Mapping[str, Any] | None = None,
        ) -> None:

            assert isinstance(excs, (tuple, list))
            assert all(isinstance(x, BaseException) for x in excs)

            if message is None:
                message = f'{len(excs)} exceptions occurred during execution'
            super().__init__(message, *excs)

            self.context = context or {}
            self.exceptions = excs

        def __str__(self) -> str:
            lines = [
                super().__str__()
            ]
            lines.extend(f'{e}\n' for e in self.exceptions)
            return ''.join(lines)


else:
    from collections import UserList

    class BaseExceptionGroup(UserList):
        """
        A container for multiple exceptions that were raised during execution
        of a single potentially long-running operation.
        """

        def __init__(
                self,
                excs: Union[
                    tuple[Exception],
                    Iterable[tuple[Exception]],
                    Sequence[Union[Exception, Tuple[Exception]]],
                ],
                message: str | None = None,
                *,
                context: Mapping[str, Any] | None = None,
        ) -> None:

            assert isinstance(excs, (tuple, list))

            if message is None:
                message = f'{len(excs)} exceptions occurred during execution'
            super().__init__(excs)

            self.context = context or {}
            self.exceptions = excs

        def __str__(self) -> str:
            lines = [
                super().__str__()
            ]
            lines.extend(e.__str__() + '\n' for e in self.exceptions)
            return ''.join(lines)

def test_base_exception_group():
    """Test the BaseExceptionGroup class."""
    try:
        raise ValueError("Oops")
    except Exception as ve1:
        try:
            raise TypeError("Oops")
        except Exception as te1:
            try:
                raise KeyError("Oops")
            except Exception as ke1:
                try:
                    raise IndexError("Oops")
                except Exception as ie1:
                    try:
                        raise ValueError("Oops")
                    except Exception as ve2:
                        try:
                            raise TypeError("Oops")
                        except Exception as te2:
                            try:
                                raise KeyError("Oops")
                            except Exception as ke2:
                                try:
                                    raise IndexError("Oops")
                                except Exception as ie2:
                                    try:
                                        with pytest.raises(BaseExceptionGroup) as ex:
                                            raise BaseExceptionGroup(
                                                [ve1, te1, ke1, ie1, ve2, te2, ke2, ie2]
                                            )
                                    finally:
                                        pass
                            finally:
                                pass
                    finally:
                        pass
            finally:
                pass
    finally:
        pass