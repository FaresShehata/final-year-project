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

@dataclass(slots=True)
class PointDataClass:
    x: int
    y: int


PointDataClass.__new__.__defaults__ = (None,) * len(PointDataClass.__annotations__)

point_data_class = PointDataClass(x=1, y=2)
point_data_class.x = 3

# Walrus Operator ============================================================

my_list = ["this is a string"]
int(my_list[0]) if len(my_list) > 0 else None

# Structural Pattern Matching ================================================

match point_data_class:
    case PointDataClass(x, _):  print(f'x={x}')
    case _:                     print('Unknown point')

# Generics =========================================================================

T           = TypeVar("T")
Container[T] = Generic[T]


class Queue(Container[T]):
    pass


queue :Queue[int]
queue.append(1)
queue.append(2)
queue.append(3)

for item in queue:
    print(item)


# Exception Groups ==============================================================

try:
    raise ValueError("Oopsie!")
except Exception:
    raise ValueError("Boom!") from Exception()

ex_group = ExceptionGroup(
    f"Multiple exceptions",
    [ValueError(), ZeroDivisionError()]
)

print_type(object())


async def main():
    task_1 = asyncio.create_task(simple_coroutine())
    await asyncio.sleep(0.5)
    task_2 = asyncio.create_task(coroutine_with_args('a', 'b'))
    # TODO - change the sleep time so we can see what happens after awaiting on `task_1`
    await asyncio.wait([task_1, task_2])
    # TODO - wait until both tasks are done before exiting the program


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    finally:
        loop.close()