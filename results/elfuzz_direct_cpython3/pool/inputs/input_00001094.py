"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

import asyncio
from collections import namedtuple

# Async/Await ================================================================

def simple_coro():
    return "Hello"


async def simple_coroutine():
    await asyncio.sleep(0.001)
    return "Hello"


async def coroutine_with_args(*args):
    await asyncio.sleep(0.001)
    return args


# Protocols ===================================================================

@dataclass(frozen=True)
class Point: ...

Point.__annotations__.update({"x": float, "y": float})

# Slots =======================================================================

@dataclass(slots=True)
class PointSlots: ...
point_slots = PointSlots(1, 2)

# Walrus Operator =============================================================

result = (await simple_coroutine()) if True else "World"
assert result == "Hello"

# Typing Generics ========================================================================

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