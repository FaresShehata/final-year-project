"""
Seed 01 — OOP, metaclasses, descriptors, decorators, context managers, generators
"""

from __future__ import annotations

import abc
import contextlib
import functools
import itertools
import operator
import sys
import types
import weakref
from typing import Any, ClassVar, Generator, Iterator, Optional, Type, TypeVar

T = TypeVar("T")

# ── Descriptors ──────────────────────────────────────────────────────────────

class TypedDescriptor:
    """Descriptor that enforces a type and optional range constraint."""

    # This class defines two abstract methods.
    @classmethod
    @abc.abstractmethod
    def validate(cls, value: Any) -> None:
        ...

    def __get__(self, instance: object, owner: object | None) -> any:
        return self._value
    
    def __set__(self, instance: object, value: Any) -> None:
        self.validate(value)
        self._value = value

    def __delete__(self, instance: object) -> None:
        del self._value


class IntTyped(TypedDescriptor):
    @classmethod
    def validate(cls, value: int) -> None:
        assert isinstance(value, int), "Not an integer!"


class FloatRangeTyped(TypedDescriptor):

    MIN_VALUE: ClassVar[float]
    MAX_VALUE: ClassVar[float]

    @classmethod
    def validate(cls, value: float) -> None:
        assert (
            cls.MIN_VALUE <= value <= cls.MAX_VALUE
        ), f"Not within range {cls.MIN_VALUE}-{cls.MAX_VALUE}"


class DTypeMeta(type):
    def __new__(
        cls: type[Dtype],
        name: str,
        bases: tuple[type[Any], ...],
        namespace: dict[str, object],
    ) -> dtype[Any]:
        if "__slots__" not in namespace or not namespace.get("__slots__", []):
            raise RuntimeError(f"Class {name} must have slots.")

        for slot_name in namespace.get("__slots__"):
            field_type = namespace[slot_name].field_type
            if not issubclass(field_type.__class__, (IntTyped, FloatRangeTyped)):
                raise TypeError(
                    f"{slot_name} must be an instance of IntTyped or FloatRangeTyped"
                )

        return super().__new__(cls,name,bases,namespace)


class Dtype(metaclass=DTypeMeta):
    pass



@DType.register
class Int(Dtype, IntTyped):
    """
    An integer with a custom validator method.

    >>> x = Int()
    Traceback (most recent call last):
      ...
    RuntimeError: Class Int must have slots.
    """

    field_type = int


@DType.register
class RangeFloat(Dtype, FloatRangeTyped):
    """
    A floating point number between a minimum and maximum values.

    >>> x = RangeFloat(min_value=-2, max_value=3)
    Traceback (most recent call last):
      ...
    AssertionError: Not within range -2-3
    """

    min_value = -sys.maxsize
    max_value = sys.maxsize

    def validate(self, value: float) -> None:
        assert self.min_value <= value <= self.max_value, f"Not within range {self.min_value}-{self.max_value}"
    
    def __str__(self) -> str:
        return f"<{self.__class__.__name__}: [{self.min_value}, {self.max_value}]>"
    



print(Int())
print(RangeFloat(0,1))
print(RangeFloat(-5,-6))

x = Int()


# ─── Context Managers ─────────────────────────────────────────────────────────

@contextlib.contextmanager
def locked_resource(lock: threading.Lock):
    try:
        lock.acquire()
        yield 
    finally:
        lock.release()



# ─── Generators ─────────────────────────────────────────────────────────────-

def fib():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a+b



fib_gen = fib()
next(fib_gen)

for _ in fib_gen:
    print(_)



# ─── Metaclasses ─────────────────────────────────────────────────────────────

class BaseMeta(type):
    pass

class MySingletonMeta(BaseMeta):
    instances: dict[str, object] = {}

    def __call__(cls, *args: list[object], **kwargs: dict[str, object        * -109 <= target <= 109
"""
from typing import List


class Solution:
    def fourSum(self, nums: List[int], target: int) -> List[List[int]]:

        result = []
        nums.sort()

        for i in range(len(nums)):
            if i > 0 and nums[i] == nums[i - 1]: continue
            for j in range(i+1,len(nums)):
                if j>i+1 and nums[j]==nums[j-1]:continue
                left=j+1
                right=len(nums)-1
                while(left<right):
                    sum=nums[i]+nums[j]+nums[left]+nums[right]
                    if sum==target:
                        temp=[nums[i],nums[j],nums[left],nums[right]]
                        result.append(temp)
                        left+=1
                        right-=1
                        while left < right and nums[left] == nums[left - 1]:
                            left += 1
                        while left < right and nums[right] == nums[right + 1]:
                            right -= 1
                    elif sum>target:right-=1
                    else:left+=1
        
        return result