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


V = lambda x, *, y=None, z=None: x + y + z  # Keyword-only arguments

W = V(1, y=2, z=3)  # Positional only arguments

X = lambda *args, **kwargs: args[0].__dict__.get(kwargs['key'], None)  # Dictionary unpacking

Y = X(M, key='age')

Z = lambda x: [sum(y) / len(y) for y in x]


# Higher order functions.
def add_one_to_all(numbers):
    return list(map(lambda n: n + 1, numbers))


add_one_to_all([1, 2, 3])


def double(x):
    return x * 2


double(4)


numbers = [1, 2, 3, 4, 5]
doubled_numbers = list(map(double, numbers))

print(doubled_numbers)

import math

powered_numbers = list(map(math.pow, numbers, range(1, 6)))

print(powered_numbers)

from collections import Counter

letters = ['b', 'c', 'd', 'd', 'e', 'f']

Counter(letters)


def is_even(number):
    return not number % 2


evens = filter(is_even, numbers)

list(evens)

names = ["Bob", "Charlie", "David", "Emily"]
filtered_names = list(filter(lambda x: len(x) < 5, names))
print(filtered_names)


def is_positive(number):
    return number >= 0


positives = list(filter(is_positive, [-1, -2, 3, 4]))

print(positives)


squares = map(lambda x: x ** 2, range(10))
print(squares)

powers_of_two = map(pow, range(10), [2] * 10)
print(powers_of_two)

maps = map(list, zip(*[[1, 2], [3, 4]]))
print(maps)

ranks = ['gold', 'silver', 'bronze']
medals = [10, 8, 6]
medalist_pairs = list(zip(ranks, medals))
print(medalist_pairs)

sorted_meadlairs = sorted(medalist_pairs, key=lambda x: x[1], reverse=False)
print(sorted_meadlairs)


def factorial(n):
    return reduce(lambda x, y: x * y, range(1, n + 1), 1)


factorial