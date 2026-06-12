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

print("Bytecode disassemblies")
assert annotated_disassembly(hot_path) == """
  3           0 LOAD_CONST               0 (0)
              2 RETURN_VALUE
"""
assert count_opcodes(hot_path) == {'LOAD_CONST': 1, 'RETURN_VALUE': 1}

print("Bytecode disassemblies with inspection")
assert annotated_disassembly(inspect.getsource(hot_path)) == """
  3           0 LOAD_FAST                0 (n)
              2 LOAD_CONST               0 (2)
              4 COMPARE_OP               6 (<)
              8 POP_JUMP_IF_FALSE       19
             10 LOAD_FAST                0 (n)
             12 LOAD_FAST                0 (n)
             14 BINARY_MULTIPLY
             16 STORE_FAST               1 (total)
             18 JUMP_ABSOLUTE            5
             21 LOAD_FAST                1 (total)
             23 LOAD_GLOBAL              0 (i)
             25 BINARY_SUBTRACT
             27 STORE_FAST               1 (total)
             29 JUMP_ABSOLUTE            5
             32 LOAD_CONST               1 (None)
             34 RETURN_VALUE
"""
assert count_opcodes(hot_path) == {'LOAD_CONST': 3, 'BINARY_MULTIPLY': 1, 'BINARY_SUBTRACT': 2, 'JUMP_ABSOLUTE': 2, 'POP_JUMP_IF_FALSE': 1, 'RETURN_VALUE': 1}

# ───── Struct and array ───────────────────────────────────────────────────────

a = array.array('b', [1, 2, 3])     # signed char
b = array.array('B', [1, 2, 3])     # unsigned char
c = array.array('i', [1, 2, 3])     # signed integer
d = array.array('I', [1, 2, 3])     # unsigned integer
e = array.array('h', [-32768, -1, 0, 1, 32767])   # short integers
f = array.array('H', [65536, 65537])   # unsigned shorts
g = array.array('l', [-2147483648, -1, 0, 1, 2147483647])   # longs
h = array.array('L', [4294967296, 4294967297])   # unsigned longs
j = array.array('q', [-9223372036854775808, -1, 0, 1, 9223372036854775807])   # longlongs
k = array.array('Q', [18446744073709551616, 18446744073709551617])   # unsigned longlongs
m = array.array('P', ['Hello'])   # pointers
n = array.array('x', [])   # voids
o = array.array('B', [ord(c) for c in "Hello"])   # bytes from string


def print_array(arr: array) -> None:
    print(textwrap.indent(str(arr.tolist()), prefix=' ' * 2))


print("\nArray:")
for arr in [a, b, c, d, e, f, g, h, j, k, m, n, o]:
    print_array(arr)

print("\nStruct:")
for typ in [struct.Struct('hh'), struct.Struct('<HH'),
            struct.Struct('>HH'), struct.Struct('<bb'), struct.Struct('<BB')]:
    s = typ.pack(e[0], e[1])
    l = struct.unpack(typ.format, s)[0]
    t = struct.unpack(typ.format, s)[1]
    print(f'{typ}: ({l}, {t})')

# ───────── Pickling ──────────────────────────────────────────────────────────

pickle.dump([1, 2, 3], open('/tmp/pickle.pkl', 'wb'))
with open('/tmp/pickle.pkl', 'rb') as fp:
    loaded = pickle.load(fp)
assert loaded == [1, 2, 3]


def dump_module(mod: types.ModuleMUL   = lambda m: lambda n: lambda f: n(m(f))
ONE   = SUCC(ZERO)
TWO   = SUCC(ONE)
THREE = SUCC(TWO)

def church_to_int(n) -> int:
    return n(lambda x: x + 1)(0)

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


add2 = compose(add3, lambda a: a - 2)


def partial(func: Callable, /, *bound_args: A, **bound_kwargs: B) -> Callable:
    """Partial application of an arbitrary number of positional and keyword arguments to a callable.

    The returned callable will accept only the remaining positional and keyword arguments.
    """
    argspec = func.__code__.co_varnames
    bound_args_names = set(bound_args)

    def partially_bound_func(*remaining_args, **remaining_kwargs):
        # Handle positional arguments first so that they are applied before keyword arguments
        bound_args_and_remaining_args = list(bound_args)
        bound_args_and_remaining_args.extend(remaining_args)
        missing_posiitional_args = max(len(argspec) - len(bound_args_names),
                                       0) - len(bound_args_and_remaining_args)
        bounded_args = tuple(
            getattr(None, arg_name) for arg_name in argspec[-missing_posiitional_args:]
        ) + tuple(bound_kwargs.get(arg_name) for arg_name in bound_args_names)

        # Combine positional arguments with default values into single sequence
        # This is done to allow us to pass it as a single argument to `func`
        kwargs_with_defaults = {**bound_kwargs, **{arg_name: None for arg_name in argspec}}
        all_args = (*bounded_args, *(kwargs_with_defaults[arg] for arg in argspec))

        return func(*all_args, *remaining_args[missing_posiitional_args:], **remaining_kwargs)

    return partially_bound_func


sum_5 = partial(sum, 5)
sum_7 = partial(sum, 7)


# ── Trampoline recursion (iterative, not tail-recursive) ──────────────────────


class TrampolinedGenerator(Iterator[A]):
    def __init__(self, generator_function: Callable[[Any], Generator]) -> None:
        self._generator = generator_function()
        self._next_yielded_value = next(self._generator)
        self._stack = [self]

    def _step(self) -> bool:
        try:
            while True:
                yield self._next_yielded_value
                self._next_yielded_value = next(self._generator)
        except StopIteration as e:
