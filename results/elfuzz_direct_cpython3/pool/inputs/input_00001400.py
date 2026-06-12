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
from typing import (TYPE_CHECKING, Any, Callable, Dict, Generic, List, NamedTuple, Optional, Protocol, Sequence, Tuple,
                    TypeVar, Union)

if TYPE_CHECKING:
    from typing_extensions import ParamSpec # noqa: F401


class ExampleEnum(enum.Enum):
    A = 'a'
    B = 'b'
    C = 'c'


@dataclasses.dataclass(frozen=True)
class DataClassExample():
    foo: str
    bar: int
    baz: float
    qux: bool


def example_dataclass_function(data_class_instance) -> None:
    data_class_instance.baz *= 3.5
    print(f'foo={data_class_instance.foo}, bar={data_class_instance.bar}, '
            f'baz={data_class_instance.baz}, qux={data_class_instance.qux}')


async def example_async_function(data_class_instance) -> None:
    await asyncio.sleep(random.randint(0, 9))
    data_class_instance.bar += 7
    print(f'foo={data_class_instance.foo}, bar={data_class_instance.bar}, '
            f'baz={data_class_instance.baz}, qux={data_class_instance.qux}')

    
T = TypeVar('T')


# https://stackoverflow.com/a/69881482
P = ParamSpec('P') 
R = TypeVar('R', covariant=True)
def curried(func: Callable[P, R]) -> Callable[[P], R]:
    if not isinstance(func, Callable): raise TypeError()
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return func(*args, **kwargs)
    return wrapper

# https://docs.python.org/3/library/typing.html#typing.Generic
class MyGeneric(Generic[T]):
    pass


# ── Generics with type variables ───────────────────────────────────────────────

def add_values(a: T, b: T, c: T) -> T:
    result = a + b + c
    assert isinstance(result, T)
    return result


# ── Generic classes ───────────────────────────────────────────────────────────

class CoercibleTo(Protocol[T]):
    def __coerce__(self, value: Any) -> T:
        ...


class GenericWithCoercion(Generic[CoercibleTo[int]]):
    ...


def myfunc(arg: CoercibleTo[bool]) -> None:
    print(f'{arg=}')
    print(f'{isinstance(arg, bool)=}')
    
    
MyList = list[str]

def get_list_element_by_index(l: MyList, index: int) -> str:
    return l[index]


# ── Structural Pattern Matching ───────────────────────────────────────────────

class MyClass:
    def __init__(self, value: float) -> None:
        self.value = value
        
    def __eq__(self, other) -> bool:
        return isinstance(other, type(self)) and self.value == other.value
    
    def __repr__(self) -> str:
        return f"MyClass({self.value})"
        
# Could be used in match statement or Union[...]
def process_number(n: Union[float, MyClass]) -> None:
    match n:
        case MyClass(value) if value < 0.0:
            print('negative')
        case MyClass(value):
            print('positive')
        case float():
            print('floating point number')
        case _:
            raise ValueError()


_foo_bar_baz_types = tuple[type[Any]]()

def process_numbers(numbers: tuple[float, ...]) -> None:
    match numbers:
        # Match any sequence of floats.
        case [first, *rest]:
            print(first, rest)
            
        # Match any sequence of only integers.
        case [int()] | [*_, int(), *_]:
            print('all ints')

        # Only match when the first element is float and all others are int.
        case [first, *rest] if isinstance(first, float):
            print(first, rest)

        # Match empty sequences.
        case []:
            print('empty')

        # Match any sequence of mixed types.
        case _:
            raise NotImplementedError()


# ── Walrus Operator ─────────────────────────────────────────────────────────    )
    return new_fn


def make_adder_from_bytecode(delta: int) -> types.FunctionType:
    """Build a function entirely from a code object (LOAD_FAST + LOAD_CONST + BINARY_OP + RETURN)."""
    # Instead of emitting raw bytecode (fragile across versions), compile source.
    src = f"def _adder(x): return x + {delta}"
    globs: dict = {}
    exec(compile(src, "<generated>", "exec"), globs)
    return globs["_adder"]


# ── Memory view & array manipulation ──────────────────────────────────────────

def arrays_and_memory_views() -> None:
    """Demonstrate how to create arrays and memory views of arbitrary types."""
    # Define some data using the standard C types we know about...
    c_int_packed = [-1, -2]
    c_float_packed = [5.5e-6, 9.7]
    c_double_packed = [math.pi, math.e]
    c_char_packed = ["a", "\x00"]

    # ...and use struct.pack to pack them into arrays.
    int_array = array.array("i")
    int_array.fromlist(c_int_packed)

    float_array = array.array("f")
    float_array.fromlist(c_float_packed)

    double_array = array.array("d")
    double_array.fromlist(c_double_packed)

    char_array = array.array("c")
    char_array.fromlist(c_char_packed)

    # Now create a buffer that points to each array's underlying memory.
    int_view = memoryview(int_array)
    float_view = memoryview(float_array)
    double_view = memoryview(double_array)
    char_view = memoryview(char_array)

    print(f"{int_view.tobytes()=} ({type(int_view).__name__}<{hex(id(int_view))})")
    print(f"{float_view.tobytes()=} ({type(float_view).__name__}<{hex(id(float_view))})")
    print(f"{double_view.tobytes()=} ({type(double_view).__name__}<{hex(id(double_view))})")
    print(f"{char_view.tobytes()=} ({type(char_view).__name__}<{hex(id(char_view))})")

    # We can read/write this as though it were an ordinary bytes-like object!
    int_view[0] = b"\xff"
    print(f"{int_view.tobytes()=} ({type(int_view).__name__}<{hex(id(int_view))})")


# ── Pickling & unpickling ────────────────────────────────────────────────────

def pickling_examples() -> None:
    # For example, use a recursive function to demonstrate pickling support for
    # submodules and nested modules.
    def sub_module_example():
        """Pickling a submodule works just like it does for other modules."""
        import pickle
        import foo.bar.baz.quux
