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
    Coroutine,
    Iterable,
    List,
    Literal,
    Optional,
    Sequence,
    Set,
    Tuple,
)

if TYPE_CHECKING:
    from .utils import Config


class TaskState(enum.Enum):
    PENDING = "Pending"
    RUNNING = "Running"
    COMPLETED = "Completed"

    @property
    def is_pending(self) -> bool: return self == TaskState.PENDING
    @property
    def is_running(self) -> bool: return self == TaskState.RUNNING
    @property
    def is_completed(self) -> bool: return self == TaskState.COMPLETED


@dataclasses.dataclass(frozen=True)
class Task:
    id_: int
    name: str
    state: TaskState
    start_time: float
    end_time: Optional[float] = None

    @classmethod
    def create_task(cls, task_id: int, name: str, state: TaskState) -> Task:
        """Create a new task with the given attributes."""
        if not isinstance(state, TaskState):
            raise ValueError("Invalid task state")
        if state.is_completed:
            raise ValueError("Task already completed")
        
        # Use freeze=False to allow modification after creation
        instance = cls.__new__(cls)
        instance.id_ = task_id
        instance.name = name
        instance.state = state
        instance.start_time = time.perf_counter()

        return instance
    
    def update_state(self, new_state: TaskState) -> None:
        """Update the state of the task."""
        if not isinstance(new_state, TaskState):
            raise ValueError("Invalid task state")

        self.state = new_state
        
        if new_state.is_completed:
            self.end_time = time.perf_counter()


class TasksManager:
    """
    A class that manages tasks.

    >>> tm = TasksManager(1, 5)
    >>> tm._tasks[1]
    {<Task(id_=1, name='task-1', state=<TaskState.RUNNING>, start_time=..., end_time=None)>}
    """

    _DEFAULT_CAPACITY = 4
    _INIT_TASKS = [Task.create_task(i, f'task-{i}', TaskState.RUNNING) for i in range(_DEFAULT_CAPACITY)]

    def __init__(self, capacity: int, initial_tasks: Optional[List[Task]] = None):

        self.capacity = capacity
        self._tasks: dict[int, set[Task]] = defaultdict(set