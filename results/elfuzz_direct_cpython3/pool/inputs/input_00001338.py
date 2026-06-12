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
    pass  # keep TYPE_CHECKING branch exercised

K = TypeVar("K")
V = TypeVar("V")
T = TypeVar("T")

# ── Enums ─────────────────────────────────────────────────────────────────────

class Status(enum.Enum):
    PENDING   = "pending"
    RUNNING   = "running"
    SUCCESS   = "success"
    FAILED    = "failed"
    CANCELLED = "cancelled"

    def is_terminal(self) -> bool:
        return self in {Status.SUCCESS, Status.FAILED, Status.CANCELLED}


class Priority(enum.IntEnum):
    LOW    = 1
    NORMAL = 5
    HIGH   = 10
    URGENT = 20


class Flag(enum.Flag):
    READ    = enum.auto()
    WRITE   = enum.auto()
    EXECUTE = enum.auto()
    RWX     = READ | WRITE | EXECUTE

    def __str__(self: Flag) -> str:
        return "".join(f"{el}" for el in sorted(el.name for el in Flag if self & el))


class Permission(enum.Enum):
    NONE       = 0o0000
    READ       = 0o4000
    WRITE      = 0o2000
    EXECUTE    = 0o1000
    ALL        = READ | WRITE | EXECUTE
    S_IRWXU    = READ | WRITE | EXECUTE
    S_IRUSR    = READ
    S_IWUSR    = WRITE
    S_IXUSR    = EXECUTE
    S_IROTH    = 0o040
    S_IWOTH    = 0o020
    S_IXOTH    = 0o010
    S_IRGRP    = 0o004
    S_IWGRP    = 0o002
    S_IXGRP    = 0o001
    S_ISUID    = 0o4000
    S_ISGID    = 0o2000
    S_ISVTX    = 0o1000
    S_IMMUTABLE= 0o4000
    S_APPEND    = 0o2000
    S_DSYNC     = 0o1000
    S_ODSYNC    = 0o0400
    S_NOATIME   = 0o0200
    S_NODIRATIME= 0o0100
    S_RELATIME  = 0o0040
    S_SYNC      = 0o0020
    S_DIRSYNC   = 0o0010
    S_CHMOD     = 0o0330
    S_CHOWN     = 0o0666
    S_CHGRP     = 0o0220
    S_CLOEXEC   = 0o0001
    S_CREAT     = 0o0002
    S_EXCL      = 0o0004
    S_TRUNC     = 0o0008
    S_APPEND    = 0o0010
    S_RENAME     = 0o0020
    S_UNLINK     = 0o0040
    S_LINK     = 0o0100
    S_MKNOD     = 0o0200
    S_SYMLINK   = 0o0400
    S_MOUNT     = 0o0600
    S_BUG      = 0o0700
    S_SOCKDATA  = 0o0100
    S_SOCKET   = 0o0200
    S_CLOEXEC   = 0o0001
    S_CREAT     = 0o0002
    S_EXCL      = 0o0004
    S_TRUNC     = 0o0008
    S_RDWR      = 0o0006
    S_O_RDONLY  = 0o0000
    S_O_WRONLY  = 0o0001
    S_O_RDWR    = 0o0002
    S_O_SYNC    = 0o0004
    S_O_NONBLOCK= 0o0008
    S_O_NDELAY  = 0o0008
    S_O_APPEND  = 0o0010
    S_O_ASYNC   = 0o0020
    S_O_FSYNC   = 0o0040
    S_O_DSYNC   = 0o0080
    S_O_RSYNC   = 0o0100
    S_O_NDELAY  = 0o0008
    S_O_DIRECT  = 0o0200
    S_O_PATH    = 0o0400
    S_IFMT      = 0o170000
    S_IFSOCK    = 0o140000
    S_IFLNK     = 0o120000
    S_IFREG     = 0o100000
    S_IFBLK     = 0o060000
    S_IFDIR     = 