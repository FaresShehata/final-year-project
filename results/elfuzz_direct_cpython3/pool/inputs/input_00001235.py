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
    return counts


print(count_opcodes(dis.Bytecode(lambda x: x ** 2)))


# ── Disassembling a module ─────────────────────────────────────────────────────

for name, func in {
    "functools": functools,
}.items():
    print(f"{name}:")
    sdis = annotated_disassembly(func)
    print(textwrap.indent(sdis, prefix="  "))
    print()


# ── Code object lookup ─────────────────────────────────────────────────────────

funcs = [
    (lambda x, y: x * y),
    lambda x, y: x * y,
    (z := lambda z: z**3)(5),
]


for fn in funcs:
    cobj = compile(fn, "<string>", "exec")

    print("\nFunction source:")
    print(cobj.co_code)
    print()

    print("\nFunction bytecode:")
    print(list(dis.get_instructions(cobj)))

    print("\nFunction globals:")
    print(inspect.getmembers(cobj.globals))

    print("\nFunction locals:")
    print(inspect.getmembers(cobj.locals))


# ── Executing a bytecode sequence ──────────────────────────────────────────────
#
# Note: The original function must be defined at the point where it's called.
#

def exec_bytecode(code: bytes, env: dict[str, Any]) -> None:
    """
    Execute a list of bytecode instructions.

    >>> env = {'a': 3}
    >>> exec_bytecode(b"\x7f\xef\xff\xd8", env)  # "\x7f\xef\xff\xd8" == b"\x7fELF"
    >>> env['a']
    3
    """
    assert isinstance(env, dict)
    locs = env.copy()
    for op, arg in dis.findlinestarts(code):
        if op.startswith("LOAD_"):
            key = op[5:].lower().replace("_", "")
            val = locs[key]
        elif op.startswith("STORE_"):
            key = op[6:].lower().replace("_", "")
            locs[key] = arg
        else:
            continue
        del code[op.argstart : op.offset]
    assert not code
    del env['__builtins__']  # Don't need built-in functions.


env = {"a": 3, "b": 42}
exec_bytecode(b"\x7f\xef\xff\xd8", env)

# ── Using ctors and dtors ─────────────────────────────────────────────────────

class CtorDtor:
    def __init__(self, value: int):
        self.value = value
        print("__new__() called with {}.".format(value))
    
    def __del__(self):
        print('__del__() called with {}'.format(self.value))

    def ctor_dtor(self) -> None:
        pass

c = CtorDtor(9)
d = CtorDtor(10)
CtorDtor.cctor()
CtorDtor.dctor()




# ── Struct and array classes ───────────────────────────────────────────────────

struct.pack('i', 1234)

array.array('L').frombytes(struct.pack('i', 1234))

assert isinstance(array.array('L'), MutableSequence)

assert isinstance(struct.Struct('<hhl').pack(-2, -1, 1, 2), bytes)
assert isinstance(struct.Struct('>hh').unpack_from(bytes([0xfimport real]))), tuple)


# ── MemoryView and MemoryView.__reduce__ ──────────────────────────────────────

# repr(mv) → "<memory at 0x...>"
mv = memoryview(bytearray(range(10)))
repr(mv)
next(iter(map(hex, mv.cast("B"))))
list(map(ord, mv.cast("B")))
list(map(chr, mv.cast("B")))

# type(mv) → <class 'mmap.mmap'>
assert isinstance(memoryview(bytearray()), mmap.mmap)

# TODO: why are these properties on memoryview? They're also on bytearray...
# memoryview.byteorder
# memoryview.itemsize


# ── Type checking using inspect.isfunction(), inspect.ismethod(), etc. ────────

inspect.ismodule(sys.modules[__name__])

inspect.isbuiltin(len)
inspect.isroutine(len)

inspect.isgeneratorfunction(generate_number())
generate_number().__iter__()
inspect.isawaitable(generate_number())

inspect.isclass(dict)
inspect.isabstract(Baz.BAR)
inspect.isdataclass(CustomDataClass)
inspect.isdatadescriptor(CustomDataClass.x)

inspect.isasyncgenfunction(async_generator_function())
isasyncio.iscoroutinefunction(coroutine_function())

inspect.iscoroutinefunction(coroutine_function())

inspect.signature(coroutine_function())


# ── Copying an object to another process — Pickle serialisation ───────────────

pickle.dumps(1234)
pickle.loads(pickle.dumps(1234)).__hash__()

with open("/tmp/foobar.pkl", "wb") as fd:
    pickle.dump((object,), fd)

with open("/tmp/foobar.pkl", "rb") as fd:
    print(pickle.load(fd).id)


# ── Importing modules from multiple packages using importlib.abc.Loader ──────

loader = importlib.util.find_spec("collections").loader
assert issubclass(loader.loader_module.__class__, importlib.abc.Loader)


# ── Creating an import context using importlib.import_module() ────────────────

importlib.import_module("os.path")


# ── Subprocess creation — subprocess.Popen or importlib.machinery.SourceFileLoader ──

subprocess.run(["ls", "-l"], check=True)
sys.executable
import os
os.system("ls -l")

"""TODO: need to test this one more"""


# ── Module reloads — importlib.reload()
import json
importlib.reload(json    assert a + ["\x00\x01"]
except TypeError:
    pass

try:
    assert a + [["\x00\x01"]]
except TypeError:
    pass

try:
    assert a + [{"one": "\x00\x01"}]
except TypeError:
    pass

try:
    assert a + [{"one": "\x00\x01"}]["one"]
except TypeError:
    pass

try:
    assert a + ("\x00\x01", "\x01\x00")
except TypeError:
    pass

try:
    assert a + [("one",)]
except TypeError:
    pass

try:
    assert a + [(("\x00\x01"),)]
except TypeError:
    pass

try:
    assert a + [{\x00\x01:
# ── TypeAlias ────────────────────────────────────────────────────────────────

JsonValue: TypeAlias = "int | float | str | bool | None | list[JsonValue] | dict[str, JsonValue]"
Seconds:   TypeAlias = float
Predicate: TypeAlias = Callable[[Any], bool]

# ── TypedDict ────────────────────────────────────────────────────────────────

class UserRecord(TypedDict, total=False):
    id:       int
    name:     str
    email:    str
    active:   bool
    metadata: dict[str, Any]


class MetricsRecord(TypedDict):
    latency_ms: float
    throughput: float
    error_rate: float


# ── Annotated constraints (runtime-checked via descriptor) ───────────────────

class _Constrained:
    """Descriptor that reads Annotated metadata to validate."""

    def __set_name__(self, owner, name):
        self.pub  = name
        self.priv = f"_{owner.__name__}__{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
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
