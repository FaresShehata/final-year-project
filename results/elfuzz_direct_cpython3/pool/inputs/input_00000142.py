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


# ── Disassembler utility functions ────────────────────────────────────────────

def get_function_bytecode(fn) -> bytes:
    return marshal.dumps(dis.Bytecode(fn).to_bytes())


def pretty_marshal(data, indent=0) -> str:
    lines = pickletools.optimize(
        pickle.dumps(marshall.loads(data), protocol=-1))
    out = ""
    for line in lines:
        if isinstance(line, pickle.PickleableScalar):
            out += f"{' ' * indent}{line}\n"
        elif isinstance(line, pickle.ExtType):
            out += (
                f'{" " * indent}b{line.code} '
                f'type {hex(line.type)}\n'
            )
        else:
            out += f'{line}'
    return out


def disassemble(code_object: types.CodeType, filename=None) -> str:
    buf = io.StringIO()

    print("\nBytecode for module:", end=" ")
    if filename is not None:
        print(filename)
    else:
        print("<anonymous>")

    for i, name in enumerate(code_object.co_names):
        print("      ", i, name)

    for i, arg in enumerate(code_object.co_varnames):
        print("      ", i, arg)

    dis.dis(code_object, file=buf)

    return buf.getvalue()


def disassemble_module(module) -> str:
    source_lines = []
    for _, name, is_built_in, filename, start_line_no, docstring in (
        importlib.util.scanned_modules(module)):
        source_lines.append(textwrap.dedent(docstring or ""))
        source_code = ''
        with open(filename, encoding='utf-8') as fp:
            source_code = fp.read()
        source_lines.extend(source_code.split('\n'))

    source_lines = [
        line.rstrip() for line in source_lines
        if line and not line.startswith('#')
    ]
    source_code = "\n".join(source_lines)

    try:
        parsed_ast_nodes = ast.parse(source_code)
    except SyntaxError:
        raise ValueError(f"Could not parse module '{module}'") from None

    source_nodes = []
    for node in parsed_ast_nodes.body:
        if isinstance(node, ast.Module):
            source_nodes.extend(ast.get_source_nodes(node))
        elif isinstance(node, ast.ImportFrom):
            pass
        elif isinstance(node, ast.Import):
            pass
        elif isinstance(node, ast.Assign):
            pass
        elif isinstance(node,
def int_to_church(n: int):
    result = ZERO
    for _ in range(n):
        result = SUCC(result)
    return result


# ── Currying & partial application ───────────────────────────────────────────

def curry(fn: Callable) -> Callable:
    """Auto-curry a function based on its arity."""
    arity = fn.__code__.co_argcount

    @functools.wraps(fn)
    def curried(*args):
        if len(args) >= arity:
            return fn(*args[:arity])
        return lambda *more: curried(*(args + more))

    return curried


@curry
def add3(a: int, b: int, c: int) -> int:
    return a + b + c


@curry
def fold_str(sep: str, left: str, right: str) -> str:
    return f"{left}{sep}{right}"


def compose(*fns: Callable) -> Callable:
    """Right-to-left function composition."""
    def composed(x):
        for f in reversed(fns):
            x = f(x)
        return x
    return composed


def pipe(*fns: Callable) -> Callable:
    """Left-to-right pipeline."""
    def piped(x):
        for f in fns:
            x = f(x)
        return x
    return piped


# ── Closures & factories ──────────────────────────────────────────────────────

def make_counter(start: int = 0, step: int = 1):
    state = [start]          # mutable cell avoids nonlocal for clarity

    def increment() -> int:
        v = state[0]
        state[0] += step
        return v

    def reset() -> None:
        state[0] = start

    def peek() -> int:
        return state[0]

    increment.reset = reset  # type: ignore[attr-defined]
    increment.peek  = peek   # type: ignore[attr-defined]
    return increment


def make_accumulator(init: float = 0.0) -> Callable[[float], float]:
    total = init

    def acc(x: float) -> float:
        nonlocal total
        total += x
        return total

    return acc


def memoize_rec(fn: Callable) -> Callable:
    """Memoisation decorator that handles recursive calls correctly."""
    cache: dict = {}

    @functools.wraps(fn)
    def wrapper(*args):
        if args not in cache:
            cache[args] = fn(*args)
        return cache[args]

    return wrapper


# ── Trampolining ──────────────────────────────────────────────────────────────

class Thunk:
    __slots__ = ("fn", "args")

    def __init__(self, fn, *args):
        self.fn = fn
        self.args = args


def trampoline(f) -> Callable:
    @functools.wraps(f)
    def wrapper(*args):
        result = f(*args)
        while isinstance(result, Thunk):
            result = result.fn(*result.args)
        return result
    return wrapper


def _even_tc(n: int, acc: bool) -> "bool | Thunk":
    if n == 0:
        return acc
    return Thunk(_odd_tc, n - 1, acc)


def _odd_tc(n: int, acc: bool) -> "bool | Thunk":
    if n == 0:
        return not acc
    return Thunk(_even_tc, n - 1, acc)


is_even_tc = trampoline(lambda n: Thunk(_even_tc, n, True))


# ── Generator coroutines (send / throw / close) ───────────────────────────────

def running_average() -> Generator[float, float, str]:
