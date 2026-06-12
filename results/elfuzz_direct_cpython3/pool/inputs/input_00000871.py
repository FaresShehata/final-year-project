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


def get_instructions(fn) -> dict:
    base_instr = "<unknown>"
    counts = count_opcodes(fn)

    def _get_instr(instr):
        if base_instr == "<unknown>" and instr.base is not None:
            base_instr = instr.base.opname
        return instr.offset, f'{instr.opname}({",".join(map(str, instr.argvals))})'

    return sorted([(v, _get_instr(instr)) for k, v in counts.items()])


def get_source(fn) -> str:
    with open(inspect.getsourcefile(fn)) as fp:
        return fp.read()


def get_docstring(fn) -> str | None:
    return fn.__doc__ or ""


def compile_fn(fn, filename="<fn>", flags=None) -> types.CodeType:
    assert isinstance(fn, types.FunctionType)
    return compile(get_source(fn), filename, "exec", flags or "exec")


def build_frame(f_globals: dict[str, Any], f_locals: dict[str, Any]) -> types.FrameType:
    return types.FrameType(
        globals=f_globals,
        locals=f_locals,
        f_back=sys._getframe(),
        f_trace=None,
        f_code=get_code_obj(type(f_globals)),
    )


def get_source_lines(obj: object) -> tuple[list[str], int]:
    nlines = obj.co_firstlineno - 1
    lines = inspect.getsourcelines(obj)[0][nlines:]
    return lines, nlines


def get_bytecode(obj: object) -> bytes:
    return marshal.dumps(obj.co_code)


def get_code_obj(obj):
    try:
        return obj.codeobj
    except AttributeError:
        return obj.func_code


def has_co_filename(obj) -> bool:
    try:
        obj.co_filename
    except AttributeError:
        return False
    else:
        return True


def _co_basename(code: types.CodeType) -> str:
    basename = code.co_filename.split("/").pop().split(".")[0].rsplit(".", 1)[0]
    return basename.capitalize() if basename != "_io" else "StdIn"


def _co_basenames(obj: object) -> set[str]:
    basename = _co_basename(obj)
    names: list[str] = []
    while basename != "std":
        names.append(basename)
        basename = _co_basename(globals()[basename])
    return set(names[::-1])


def co_filenames(obj: object) -> tuple[str, ...]:
    return tuple(_co_basenames(obj))


def get_freevars(obj: object) -> list[str]:
    return [var.name for var in obj.co_varnames]


def get_names(obj: object) -> tuple[str, ...]:
    return tuple(var.name for var in obj.co_names)


def get_argcount(obj: object) -> int:
    return obj.co_argcount


def get_kwonlyargcount(obj: object) -> int:
    return obj.co_kwonlyargcount


def get_nlocals(obj: object) -> int:
    return obj.co_nlocals


def get_stacksize(obj: object) -> int:
    return obj.co_stacksize


def get_constants(obj: object) -> tuple[Any, ...]:
    return tuple([const.value for const in obj.co_consts])


def get_fragments(obj: object) -> list[tuple[int, str]]:
    lines: list[tuple[int, str]] = []
    for offset, line in enumerate(obj.co_lnotab.decode(errors="ignore")):
        if line >= 0x80:
            break
        elif line < 0:
            continue
        else:
            lines.append((offset * line // 4, f"# {line}"))
    return lines


def get_comments(obj: object) -> list[str]:
    comments: list[str] = []
    for offset, comment in obj.co_lnotab.decode(errors="ignore"):
        if offset < 0:
            continue
        if comment & ~0xFF:
            comment &= 0xFF
            comments.append(comment_to_comment(offset, comment))
        elif    from typing_extensions import NotRequired as NotRequired_T

    class Protocol_T(Protocol): pass
    class TypedDict_T(TypedDict): pass
    class ForwardRef_T(FutureWarning): pass
    class NotRequired_T(DeprecationWarning): pass
    class Concatenate_T(DeprecationWarning): pass
    class ParamSpec_T(DeprecationWarning): pass
    class Self_T(DeprecationWarning): pass

from unicodedata import (
    category,
    normalize,
)

from rich.console import ConsoleRenderable
from rich.highlighter import Highlighter
from rich.style import Style
from rich.text import Text

try:
    from rich.pretty import Pretty
except ImportError:
    """pretty module not available on pypy"""
    def Pretty(obj: Any) -> str:  # pragma: no cover
        return repr(obj)


if sys.platform.startswith("win"):
    import msvcrt

    def raw_input(prompt: Optional[str]=None) -> str:
        msvcrt.putch(b"\r\n")
        return input()


class LazyProperty(property):
    """
    Property that's evaluated only once per instance and then replaces itself with an ordinary attribute.

    This allows you to have properties do things like lazy-loading DB models without having to put the logic inside
    the property itself.

    Example:

        >>> class Dog:
        ...     name = LazyProperty(lambda self: "Spot")

        >>> d = Dog()
        >>>        if obj is None:
            return self
        return getattr(obj, self.priv, None)

    def __set__(self, obj, value):
        hints = get_type_hints(type(obj), include_extras=True)
        ann   = hints.get(self.pub)
        if ann and hasattr(ann, "__metadata__"):
            for constraint in ann.__metadata__:
                if callable(constraint):
                    if not constraint(value):
                        raise ValueError(f"{self.pub}={value!r} fails constraint")
        setattr(obj, self.priv, value)


def positive(x) -> bool:
    return isinstance(x, (int, float)) and x > 0

def short_str(x) -> bool:
    return isinstance(x, str) and len(x) <= 20


class Sensor:
    reading: Annotated[float, positive] = _Constrained()   # type: ignore[assignment]
    label:   Annotated[str,   short_str] = _Constrained()  # type: ignore[assignment]

    def __init__(self, label: str, reading: float):
        self.label   = label
        self.reading = reading

    def __repr__(self):
        return f"Sensor({self.label!r}, {self.reading})"


# ── NamedTuple ────────────────────────────────────────────────────────────────

class Span(NamedTuple):
    start: int
    end:   int
    label: str = ""

    def length(self) -> int:
        return self.end - self.start

    def overlap(self, other: Span) -> int:
        return max(0, min(self.end, other.end) - max(self.start, other.start))


# ── numbers ABC ──────────────────────────────────────────────────────────────

class Rational(numbers.Rational):
    """Minimal rational backed by integer numerator/denominator."""

    def __init__(self, num: int, den: int = 1):
        if den == 0:
            raise ZeroDivisionError
