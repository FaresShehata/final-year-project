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
        new_co, fn.__globals__, new_name, fn.__defaults__, fn.__closure__ or None
    )
    return new_fn


def get_code_object(fn: types.FunctionType) -> types.CodeType:
    return fn.__code__

# ── Low-level data structures and utilities ───────────────────────────────────

def print_struct_info(struct_type: type[ctypes.Structure]) -> None:
    print(f"struct {struct_type.__name__} contains:")
    for field in struct_type._fields_:
        name, ctype = field
        size = ctypes.sizeof(ctype)
        offset = ctypes.addressof(ctypes.create_string_buffer(b"\x00", size))
        start = hex(offset.value)[2:]
        end = (hex(offset.value + size - 1)[2:])
        print("  ", f"{name}:{size} bytes [{start}:...{end}]")

def print_array_info(array_type: type[array.array]) -> None:
    print(f"array {array_type.__name__} contains:")
    dtype = getattr(array_type, "dtype")
    for value in [v for v in array.array("i")]:
        print("  ", f"{value:{len(str(-9**9))}}")


# ── Pickle ───────────────────────────────────────────────────────────────────

class CustomPickler(pickle.Pickler):
    def find_class(self, module_name: str, class_name: str) -> Any:
        # try to load from the current module first
        try:
            return super().find_class(module_name, class_name)
        except AttributeError:     # pragma: no cover
            pass
        # then try to find it as an attribute on the global namespace
        try:
            mod = sys.modules[module_name]
            cls = getattr(mod, class_name)
            return cls
        except Exception:
            raise pickle.UnpicklingError(f"{module_name}.{class_name}")


def pprint_dumps(dump: Any) -> None:
    p = CustomPickler(io.BytesIO(), protocol=pickle.HIGHEST_PROTOCOL)
    p.dump(dump)
    dump_bytes = p.stream.getvalue()
    print(pickletools.dump_all(dump_bytes))


def custom_persistent_loads(data: bytes) -> Any:
    loader = CustomLoader()
    obj = loader.load_global(data)
    return obj


class CustomLoader(pickle.Unpickler):
    def find_class(self, module_name: str, class_name: str) -> Any:
        try:
            return super(CustomLoader, self).find_class(module_name, class_name)
        except AttributeError:   # pragma: no cover
            pass
        try:
            mod = sys.modules[module_name]
            cls = getattr(mod, class_name)
            return cls
        except Exception:
            raise pickle.UnpicklingError(f"{module_name}.{class_name}")


def custom_reconstruct(cls: type[Any], args: tuple[Any, ...], kwds: dict[str, Any]) -> Any:
    mod_name, clz_name = cls.__module__, cls.__qualname__
    try:
        mod = sys.modules[mod_name]
        cls = getattr(mod, clz_name)
    except Exception:
        raise pickle.UnpicklingError(f"{mod_name}.{clz_name}")
    obj = cls(*args, **kwds)
    return obj


# ── CopyReg and Marshal ───────────────────────────────────────────────────────

def add_copy_reg_hook(caller: types.ModuleType) -> None:
    hook1 = add_copy_reg_hook
    def copy_reg(reconstructor=None):
        if reconstructor is not None:
            caller.reconstructor = reconstructor
        return hook1
    caller.copy_reg = copy_reg
    setattr(copy_reg, "__doc__", copy_reg.__doc__)


def add_marshal_hook(marshaller: types.ModuleType) -> None:
    hook1 = add_marshal_hook
    def marshal_dump(obj, fp):
        marshaller.fp = fp
        marshaller.obj = obj
        hook1()
    marshaller.marshal_dump = marshal_dump
    setattr(marshal_dump, "__doc__", marshal_dump.__doc__)


# ── Importing modules ────────────────────────────────────────────────────────

def import_module_with_as(name: str, alias: str) -> None:
    import_module