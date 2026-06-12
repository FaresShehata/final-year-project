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


def main():
    
    awaitable_example()
    protocols_example()
    
    example_data_classes()


# Awaitables -------------------------------------------------------------

async def wait_for(seconds: float) -> None:
    await asyncio.sleep(seconds)


async def get_random_number(min_num: float, max_num: float) -> float:
    return random.uniform(min_num, max_num)


async def run_async_tasks(tasks: Sequence[Callable[..., Any]]) -> None:
    tasks_to_run = []
    for task in tasks:
        if asyncio.iscoroutinefunction(task):
            tasks_to_run.append(asyncio.ensure_future(task()))
        else:
            raise TypeError('task must be a coroutine function')
            
    done, pending = await asyncio.wait(tasks_to_run, return_when=asyncio.FIRST_COMPLETED)
    for future in done:
        print(future.result())

        
def awaitable_example():
    @dataclasses.dataclass(frozen=True)
    class Task(NamedTuple):
        name: str
        start_time: float
        
    now = time.perf_counter()
    tasks = [
        Task(
            name='Wait for 5 seconds',
            start_time=now + 5.0,
        ),
        Task(
            name='Get number between 1 and 10',
            start_time=now + 3.0,
        ),
        Task(
            name='Do more stuff...',
            start_time=None,
        )
    ]
    
    results = []
    while len(results) < len(tasks):
        finished_task = False
        for i, task in enumerate(tasks):
            if not finished_task and task.start_time is not None:
                if task.start_time <= time.perf_counter():
                    results.append(await task.function())
                    finished_task = True
                    
        if not finished_task:
            await asyncio.sleep(0.05)

    print(results)
    
    
# Protocols ----------------------------------------------------------------    

class IterableProtocol(Protocol[T]):
    def __iter__(self) -> Iterator[T]: ...
        
        
@dataclasses.dataclass(frozen=True)
class Item:
    key: int
    
    @property
    def value(self):
        return self.key * 2
    
    
def protocols_example():
    items = [Item(i) for i in range(10)]
    
    count_by_key = {}
    for item in items:
        count_by_key.setdefault(item.value, 0)
        count_by_key[item.value] += 1
        
        
    # generic protocol with type variable
    T = TypeVar('T')
    class SupportsMagicMethod(Generic[T], Protocol):
        def __magic_method__(self, other: T) -> bool: ... 
        
        @classmethod
        def __subclasshook__(cls, subclass: type) -> bool: ...
        
        
    def do_magic_method(item_1: SupportsMagicMethod[int], item_2: SupportsMagicMethod[int]) -> bool:
        return item_1.__magic_method__(item_2)
        
    
# data classes ---------------------------------------------------------------

class Person(dataclasses.dataclass):
    name: str
    age: int
    phone_numbers: List[str]
    email: Optional[str] = None 


def example_data_classes():
    person = Person('John Doe', 30, ['+1-867-5309'], email='john.doe@example.com')