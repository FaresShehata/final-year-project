"""
Seed 03 — Functional programming: closures, higher-order functions, comprehensions,
          generators, coroutines (send/throw/close), itertools, functools,
          decorators, context managers
"""


def gcd(a: int, b: int) -> int:
    """Euclidean algorithm for greatest common divisor."""
    while a != 0 and b != 0:
        if a > b:
            a %= b
        else:
            b %= a
    return max((a + b))


gcd(48, 18)


A = [1, 2, 3]
B = [x + 1 for x in A]

C = []
for x in A:
    C.append(x + 1)

D = set(A)
E = frozenset(B)
F = {x ** 2 for x in D}

G = dict()
for i in range(len(D)):
    G[i] = D.pop()

H = sum([i ** 2 for i in D])

I = lambda n: str(n).zfill(3)
J = I(98765)

K = lambda n=6, m="hello": f"{n} {m}"
L = K("world")

M = {"name": "John", "age": 30}


class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age


N = Person(name="Alice", age=25)


O = lambda x, y, z=5: x + y + z


P = O(1, 2, 3)


Q = lambda *args: args  # Tuple unpacking.


R = lambda **kwargs: kwargs.get('key', 'default')  # Dict unpacking.

S = lambda x: [y for y in x]  # List comprehension
T = S(range(10))
U = sorted(T, reverse=True)


V = lambda x, *, y=None, z=None: x + y + z


W = V(5, 2, z=3)  # Only one argument is required here, so it's possible to omit the second parameter.

X = V(z=3)(1, 2)  # Even though we don't provide any arguments, the function can be called with positional parameters.

Y = lambda x, y: x % y == 0
Z = Y(10, 2)  # True


AA = lambda x, y=lambda x: x: x + y(x)  # Recursive call


BB = AA(lambda x: x**2)
CC = BB(5)

DD = lambda x=lambda x: x*2: x(lambda x: x+1)(5)


EE = BB(CC)

FF = lambda x: lambda y: x + y
GG = FF(2)(3)

HH = lambda x: lambda y: lambda z: x + y + z
II = HH(1)(2)(3)


JJ = lambda x: lambda y: lambda z: x + y + z
KK = JJ(1)(2)(3)

LL = lambda x, y, z: x + y + z
MM = LL(1, z=2)(3)  # Positional only parameters are not allowed here. There must be only two arguments.

NN = lambda x, y, /: x + y
OO = NN(1, 2)  # Keyword-only parameters are not allowed here.


@decorator
def func():
    pass


func()


print(func.__wrapped__())


async def coroutine():
    await None


coroutine.send(1)


async def co():
    print(await None)


co.send(None)


try:
    next(co())
except StopIteration as e:
    print(e.value)


def decorator(f):
    async def wrapper(*args, **kwargs):
        try:
            result = await f(*args, **kwargs)
            return result
        except Exception as exc:
            raise exc
    return wrapper


from typing import Callable

AsyncFunc = Callable[..., Awaitable]


async def make_request(url: str) -> bytes:
    pass


get_async = decorator(make_request)


@make_request
async def get_sync(url: str) -> bytes:
    pass


get_sync("/")


import asyncio


async def main_coro():
    ...


main_task = asyncio.create_task(main_coro())

with main_task:


async def my_coro1():
    ...  # Do something...


async def my_coro2():
    ...  # Do something...


await asyncio.gather(my_coro1(), my_coro2())


async def countdown_task(number: int, period: float):
    while number > 0:
        print(number)
        await asyncio.sleep(period)
        number -= 1


async def countdown_tasks(numbers: list[int], period: float) -> None:
    tasks = [
        asyncio.create_task(countdown_task(number, period)) for number in numbers
    ]
    await asyncio.wait(tasks)


countdown_tasks(list(range(10)), 0.2)


async def gen_consume():
    task = asyncio.create_task(gen_produce())
    await task


async def gen_produce():
    yield 1
    yield 2
    yield 3
    await asyncio.sleep(1)


gen_consume()


async def sleep(delay: float) -> None:
    await asyncio.sleep(delay)


async def run_tasks_with_timeout(max_delay: int = 10) -> None:
    tasks = [sleep(i) for i in range(max_delay)]
    await asyncio.wait_for(asyncio.gather(*

# Use the generator from the previous seed to calculate prime numbers.
prime_generator = primes()