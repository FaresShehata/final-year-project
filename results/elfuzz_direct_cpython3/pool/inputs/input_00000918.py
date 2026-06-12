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
import marshal
import pickle
import pickletools
import struct
import sys
import textwrap
import tracemalloc
import types
import weakref
from typing import Any

# ── Bytecode introspection ────────────────────────────────────────────────────

def annotated_disassembly(fn) -> str:
    buf = io.StringIO()
    dis.dis(fn, file=buf)
    return buf.getvalue()


def count_opcodes(fn) -> dict[str, int]:
    counts: dict[str, int] = {}
    for instr in dis.get_instructions(fn):
        counts[instr.opname] = counts.get(instr.opname, 0) + 1
    return dict(sorted(counts.items()))


def hot_path(n: int) -> int:         # deliberately simple for clear bytecode
    total = 0
    for i in range(n):
        if i % 2 == 0:
            total += i * i
        else:
            total -= i
    return total


# ── Code object surgery ───────────────────────────────────────────────────────

def clone_with_name(fn: types.FunctionType, new_name: str) -> types.FunctionType:
    """Return a copy of fn with a different __name__ embedded in its code."""
    co = fn.__code__
    # Python 3.8+ .replace() API
    new_co = co.replace(co_name=new_name)
    new_fn = types.FunctionType(
        new_co, fn.__globals__, new_name, fn.__defaults__, fn.__closure__
    )
    new_fn.__dict__.update(fn.__dict__)
    return new_fn


def change_code_object(fn: types.FunctionType, newco: types.CodeType) -> None:
    """Replace the code attribute of a function's .__code__ with newco."""
    fn.__code__ = newco


def add_to_globals(fn: types.FunctionType, to: set[str]) -> None:
    """Add all names from fn.__globals__ that aren't already in 'to' to 'to'."""
    for name, value in fn.__globals__.items():
        if isinstance(value, types.FunctionType):
            continue
        if name not in to:
            to.add(name)



# ── Types and protocols ───────────────────────────────────────────────────────

_T = TypeVar('_T')
_Sensor = TypeVar('_Sensor', bound='Sensor')


class Sensor(_Protocol[_Sensors]):     # can be used as bounds on generic types
    reading: _Annotated[float, positive]


_Annotated = TypeVar('_Annotated', bound=Tuple[Any, ...])


def _validate_annotation(annotation: Any) -> TypeGuard[Tuple[Any, ...]]:
    return isinstance(annotation, tuple) and len(annotation) == 2 \
           and annotation[0] is Annotated \
           and isinstance(annotation[1], tuple) \
           and len(annotation[1])>0 \
           and all(isinstance(a, tuple) and len(a)==2 for a in annotation[1])

@overload
def Annotated[T_co, Annos:_Annotated](_annos:Annos) -> T_co:
    ...

@overload
def Annotated[T_co, Annos:_Annotated](_annos:Any) -> T_co:
    ...

def Annotated[T_co, Annos:_Annotated](annotation: Annos | None = None) -> Callable[[T_co], T_co]:
    """Like @typing.overload but for non-generic types.

    >>> @Annotated[int, "a", ("b", "c")]
    ... class Foo:
    ...     pass
    """
    if annotation is None or _validate_annotation(annotation):
        return lambda t: t
    elif _validate_annotation(annotation[1]):
        return lambda t: t
    else:   # nested Annotated; recurse!
        return Annotated[tuple(Annotated(t, l) for t,l in zip(annotation[1:], annotation[0]))]

_Region = Final[None | Tuple[bytes, ...]] = field(default=None)


def region(buf: bytes, start: int, end: int) -> Region:
    """Region like mmap.mmap(). With a buffer instead of an address.
    
    If you have a byte string, use `bytes.region()` instead.
    """
    assert start <= end
    return make_region((buf, (start, end)))


def make_region(region:Region) -> Region:
    if not isinstance(region, tuple):       # check for bytes.buffer subclass?
        region = (region, (0, len(region)))
    return types.SimpleNamespace(start=region[1][0],
                                 stop=region[1][1],
                                 data=region[0])
    

_MemoryViewLike = TypeVar("_MemoryViewLike", bound="types.MemoryView")

def memview(typ: type[_MemoryViewLike], *, obj: MemoryViewLike) -> _MemoryViewLike:
    """Create a new memory view like mmap.mmap().
    
    This could be implemented using PyMem_MakeArrayView(), but it would require
    C extension support in the interpreter.
    """
    raise NotImplementedError()



# ── System internals ──────────────────────────────────────────────────────────

# https://docs.python.org/3/library/sys.html#sys.intern
interned_strings = {item.strip(): item for item in open('data/intern.txt')}
assert sys.intern("hello") in interned_strings
assert sys.intern(sys.intern("world")) in interned_strings
del sys.interned_strings


# ── Frame inspection ──────────────────────────────────────────────────────────

def getframe_info(frame: types.FrameType) -> str:
    """Get source line info for a given frame as a human-readable string.
    
    The frame must exist in the current execution stack at the time this 
    function is called.
    """
    return f"{format_address(frame.f_lineno)}\n{getsourceframe(frame).strip()}"

def format_address(line_number:int) -> str:
    """Format a line number into a string suitable for printing."""
    filename:str = getattr(frame.f_trace, "__filename__")
    return f"File \"{filename}\", line {line_number}"


# ── Garbage collection and