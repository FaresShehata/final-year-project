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
        
        
    # generic protocol with type variable T
    class CountByKey(Generic[T]): 
        def __init__(self):
            self._count_by_key: Dict[int,int]
            
    count_by_key = CountByKey()
    
    for item in items:
        count_by_key.setdefault(item.value, 0)
        count_by_key[item.value] += 1
            
    assert count_by_key == count_by_key._count_by_key
            


# Data Classes -------------------------------------------------------------   
  
@dataclasses.dataclass(frozen=True)
class DataClassWithDefaults:
    foo: int = 4
    bar: str = 'bar'
    baz: float = -999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999