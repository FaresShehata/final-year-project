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
        
    tasks = [
        lambda x=3.5: wait_for(x),
        lambda y=10.8, z=6.7: sum((x, y, z)),
        lambda num: get_random_number(0.0, 10.0), 
    ]
    
    
    print('\n--- Awaitable tasks ---\n')
    for task in tasks:
        print(f'{type(task).__name__}({repr(task.__defaults__)})')

    print('\n=== Running the tasks ===\n')
    tasks_names = [str(type(t).__name__).replace('_', ' ').capitalize().strip() for t in tasks]
    tasks_start_time = [time.time()] * len(tasks)
    tasks_result = []
    total_elapsed_time = 0
    
    while True:
        elapsed_time = time.time() - tasks_start_time.pop(0)
        total_elapsed_time +=