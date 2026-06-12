"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

import asyncio
from collections import namedtuple

# Async/Await ================================================================

def simple_coro():
    return "Hello"


async def coroutine_with_args(arg_a: str, arg_b: int):
    print(f'{arg_a} {arg_b}')


# Protocols ===================================================================

class HasArea:

    @property
    def area(self) -> float:
        raise NotImplementedError()


Rectangle = namedtuple("Rectangle", ("width", "height"))
Circle   = namedtuple("Circle"  , ("radius"))

def get_area(shape: HasArea):
    return shape.area


rectangle = Rectangle(width=3, height=4)
circle    = Circle(radius=5)

assert round(get_area(rectangle)) == 12
assert round(get_area(circle))     == 78.54

# Data Classes ==================================================================
# https://docs.python.org/3/library/dataclasses.html

@dataclass(unsafe_hash=True)
class Point:
    x: int
    y: int

p = Point(x=1, y=2)
print(p.x + p.y) # >>> 3

# Slots ====================================================================================

# https://docs.python.org/3/reference/datamodel.html#slots

class PointSlots:
    __slots__ = ["x", "y"]

    def __init__(self, x, y):
        self.x = x
        self.y = y

pt_s = PointSlots(1, 2)

# Structural Pattern Matching ============================================================

person = {"name": "John", "age": 30}

match person:
    case {"name": name, "age": age}:
        print(f"{name} is {age}")
    case _:
        print("No match")

class Dog:
    pass

dog = Dog()
if isinstance(dog, Dog):
    print('it\'s a dog')

# Walrus Operator =======================================================================
# https://www.python.org/dev/peps/pep-0572/

# Python >= 3.8 only
a = [1, 2, 3]
b = [4, 5]

c = next((i for i in a if (v := i * 2)), None)