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
        else:  # a < b
            b %= a

    return max(a, b)


@gcd
def find_gcd(*numbers: int) -> int:
    """Find greatest common divisor of several integers."""

@gcd
def list_gcd(list_of_numbers: list[int]) -> int:
    """Calculate GCD of all numbers in the list."""


# Use the generator from the previous seed to calculate prime numbers.
prime_generator = primes()