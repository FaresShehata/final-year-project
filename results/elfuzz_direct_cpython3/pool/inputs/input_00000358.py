"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import bisect
import dataclasses
import enum
import heapq
import json
import random
import re
import time
from collections import Counter, defaultdict, deque
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    ClassVar,
    Generic,
    Iterator,
    Literal,
    Protocol,
    TypeVar,
    overload,
    runtime_checkable,
)

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence
    from typing_extensions import Self

    from .types import *
    from .utils import *


# ── Utilities ─────────────────────────────────────────────────────────────────

def is_empty(obj: object) -> bool:
    if obj is None or len(obj) == 0:
        return True
    elif hasattr(obj, "__getitem__"):
        for item in obj:
            return False
        return True