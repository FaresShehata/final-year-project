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

T = lambda x: [(y, type(y)) for y in x]  # Nested list comprehension

U = lambda x: {f'y_{k}': v for k, v in enumerate(x)}  # Dictionary comprehension


V = lambda x, y: x + y  # Lambda function with two parameters.

# Multiply every element in the list `numbers` by 2.
[lambda x: x * 2(number) for number in numbers]


# Use the generator from the previous seed to calculate prime numbers.
prime_generator = primes()