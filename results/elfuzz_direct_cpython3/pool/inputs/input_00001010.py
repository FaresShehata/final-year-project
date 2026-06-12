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
    TIMEDOUT  = "timedout"

    @staticmethod
    def status_of(obj: object) -> Status:
        if isinstance(obj, dict): 
            if obj.get(Status.PENDING.value) is not None:
                return Status.PENDING
            
            elif obj.get(Status.RUNNING.value) is not None:
                return Status.RUNNING
                
            elif obj.get(Status.SUCCESS.value) is not None \
                 or obj.get(Status.CANCELLED.value) is not None \
                 or obj.get(Status.TIMEDOUT.value) is not None:
                
                return Status(obj.get(Status.SUCCESS.value))
                
        elif isinstance(obj, list): 
            if len(obj) == 0:
                return Status.PENDING
            
            elif any([isinstance(x, dict) and x.get(Status.SUCCESS.value) is not None \
                      for x in obj]):
                return Status.SUCCESS
                
            elif any([isinstance(x, dict) and x.get(Status.FAILURE.value) is not None \
                      for x in obj]): 
                return Status.FAILED
            
            elif all([isinstance(x, dict) and x.get(Status.RUNNING.value) is not None \
                      for x in obj]):
                return Status.RUNNING
            
            else:
                return Status.CANCELLED
                
        else:
            return Status.UNKNOWN
    
            
            
@runtime_checkable     
class AsyncIterable(Protocol[K]): 
    async def __aiter__(self) -> AsyncIterator[K]:
        ...


@runtime_checkable     
class AsyncIterator(Protocol[K]): 
    def __anext__(self) -> Awaitable[K]:
        ...


@runtime_checkable     
class AsyncContextManager(Protocol):
    async def __aenter__(self) -> Any:
        ...

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        ...


# ── Generics ────────────────────────────────────────────────────────────────

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
    

def func_with_default_args(arg1=1, arg2=int()):
    pass


def func_with_variadic(*args, **kwargs):
    pass


async def main():
    print(asyncio.iscoroutinefunction(func_with_default_args))
    print(asyncio.iscoroutinefunction(func_with_variadic))

    await main()
    print('done')
    
def main_await():
    loop = asyncio.new_event_loop()
    future = asyncio.Future()

    def callback(result):
        future.set_result(result)

    loop.call_later(5.0, lambda: loop.call_soon(callback, True))

    assert(loop.run_until_complete(future) == True)


# ── Classes ────────────────────────────────────────────────────────────

class NonGenericClass:
    pass

class GenericClass[T]:
    def __init__(self, value: T) -> None:
        self._value = value
        
    def get(self) -> T:
        return self._value
        
        
class GenericClassWithDefault[T=NonGenericClass]:
    def __init__(self, value: T) -> None:
        self._value = value
        
    def get(self) -> T:
        return self._value


generic_class = GenericClass[NonGenericClass]()
print(generic_class.get())

generic_class = GenericClass[int]()
print(generic_class.get())

generic_class = GenericClass[float](3.5)
print(generic_class.get())


generic_class_with_default = GenericClassWithDefault[int]()
print(generic_class_with_default.get())


generic_class_with_default = GenericClassWithDefault[str]()
print(generic_class_with_default.get())


# ── Exceptions ────────────────────────────────────────────────────────────

try:
    raise ValueError
except ValueError as e:
    print(e.args[0])


class CustomException(Exception):
    def __init__(self, message='Custom message', code=-1) -> None:
        super().__init__()
        self.message = message
        self.code = code
        
    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.message} ({self.code})"


raise CustomException()


# ── Types ────────────────────────────────────────────────────────────

AnyType = TypeVar('Any')
GenericType = TypeVar('Type')


class GenericExample(Generic[AnyType, GenericType]):
    def __init__(
        self,
        a: AnyType,
        b: GenericType = GenericType,
    ) -> None:
       