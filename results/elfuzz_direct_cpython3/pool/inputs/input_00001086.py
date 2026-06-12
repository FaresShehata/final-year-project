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

print(annotated_disassembly(lambda x: x + 1))

# ── dis module ────────────────────────────────────────────────────────────────

for i in range(ord("a"), ord("z") + 1):
    print(f"ord({i}): {dis.opname[i]}")
    print(f"{i}: {dis.opname[i]}")


# ── Code Objects ──────────────────────────────────────────────────────────────


def func(a, b):
    pass


assert func.__code__.co_argcount == 2

func_code = func.__code__
assert isinstance(func_code.co_consts, tuple)

assert len(func_code.co_names) > 56

# ── ctypes ────────────────────────────────────────────────────────────────────

intp_t = ctypes.POINTER(ctypes.c_int)

s = struct.Struct("<hh")
v = s.pack(7, 11)
print(v)
print(struct.unpack_from(s.format, v))  # <- unpack_to



# ── Array ─────────────────────────────────────────────────────────────────────

# py3k
arr = array.array("b", [0])
arr.append(-99)
assert arr.typecode == "b"
arr.extend(range(1, 4))
assert bytes(arr) == b"\x00\x0e\x0d\xff"


# ── Struct ────────────────────────────────────────────────────────────────────

struct = struct.Struct("<iiii")
data = struct.pack(
    123,
    *[sum(i for i in range(j)) for j in range(1, 5)],
)
assert data == b"\x7b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00# pickle.dump(date, open("obj.pkl", "wb"))

with open("obj.pkl", "rb") as fp:
    obj = pickle.load(fp)                          # <3>
    print(obj)

arr = array.array("d", [-2.1, -3.1, -4.1])
pickle.dump(arr, open("arr.pkl", "wb"))            # <4>


with open("arr
    @abc.abstractmethod
    def perimeter(self) -> float: ...

    @CachedProperty
    def label(self) -> str:
        return f"{type(self).__name__}(color={self.color})"

    def __repr__(self) -> str:
        return f"{type(self).__name__}(area={self.area():.4f})"

    def __lt__(self, other: Shape) -> bool:
        return self.area() < other.area()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Shape):
            return NotImplemented
        return type(self) is type(other) and self.area() == other.area()

    def __hash__(self) -> int:
        return hash((type(self).__name__, round(self.area(), 8)))


import math

class Circle(Shape):
    radius: float = TypedDescriptor(float, lo=0.0)  # type: ignore[assignment]

    def area(self) -> float:
        return math.pi * self.radius**2

    def circumference(self) -> float:
        return 2 * math.pi * self.radius

    def __init__(self, *, color: str = "black"):
        super().__init__(color=color)


class Rectangle(Shape):
    width:  float = TypedDescriptor(float, lo=0.0)
    height: float = TypedDescriptor(float, lo=0.0)

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)

    def __init__(self, *, color: str = "black"):
        super().__init__(color=color)


class Triangle(Shape):
    base:   float = TypedDescriptor(float, lo=0.0)
    height: float = TypedDescriptor(float, lo=0.0)

    def area(self) -> float:
        return 0.5 * self.base * self.height

    def perimeter(self) -> float:
        return self.base + self.height + self.hypotenuse()

    def hypotenuse(self) -> float:
        return ((self.base / 2)**2 + (self.height / 2)**2)**0.5

    def __init__(self, *, color: str = "white"):
        super().__init__(color=color)


class Square(Rectangle):
    def __init__(self, *, color: str = "red"):
        super().__init__(width=self.side_length, height=self.side_length)

    @property
    def side_length(self) -> float:
        return self.width

# ── MemoryView & Bytes I/O

memory_view = memoryview(b"hello world")
try:
    memory_view[0] = 1
except TypeError:
    print("TypeError")
else:
    print("Shouldn't happen")
    
print(memory_view.tobytes())
byte_array = bytearray(memory_view)
print(byte_array)




<|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|>    Literal,
    NamedTuple,
    Never,
    ParamSpec,
    TypeAlias,
    TypedDict,
    TypeVar,
    get_type_hints,
)

T  = TypeVar("T")
P  = ParamSpec("P")

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

# ── ClassVar ─────────────────────────────────────────────────────────────────

class MyList(list):
    items_per_line: ClassVar[int] = 3
    item_separator: ClassVar[str] = ", "

# ── ClassVar ─────────────────────────────────────────────────────────────────

class MyClass:
    attribute_1: ClassVar[str] = "Hello"
    attribute_2: ClassVar[str] = "World"

# ── ClassVar ─────────────────────────────────────────────────────────────────

class MyString(str):
    def upper_case(self) -> str:
        return self.upper()

# ── VarArg and Kwarg ─────────────────────────────────────────────────────────

def var_arg_func(*args: Any) -> None:
    print(args)
    for arg in args:
        print(arg.__class__.__name__)

var_arg_func()
var_arg_func(1)
var_arg_func(True)
var_arg_func([1, 2])
var_arg_func(MyClass())
var_arg_func(MyString("abc"))

def kwarg_func(**kwds: Any) -> None:
    print(kwds)
    for key, val in kwds.items():
        print(key, val.__class__.__name__)

kwarg_func()
kwarg_func(name="Alice", age=30)
kwarg_func(person={"name": "Bob", "age": 25})
kwarg_func(items=[1, 2, 3])

# ── overload --- (Optional[Tuple[Any, ...]]) ─────────────────────────────────

from typing import overload

@overload
def my_function(param: tuple[int, str]) -> str: ...
@overload
def my_function(param: tuple[int, ...]) -> int: ...

def my_function(param: tuple[int, ...]) -> int:
    return sum(param)

my_tuple = (1, 2, 3)
print(my_function(my_tuple))

# ── Annotated ────────────────────────────────────────────────────────────────

def validate_string(value):
    try:
        repr(value)
    except:
        raise ValueError(f"{value!r} cannot be represented as a string")


def initialize(obj, cls, **kwargs):
    for attr, value in kwargs.items():
        if hasattr(cls, attr):
<|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|>                        raise ValueError(f"{self.pub}={value!r} fails constraint")
        setattr(obj, self.priv, value)


def positive(x) -> bool:
    return isinstance(x, (int, float)) and x > 0

