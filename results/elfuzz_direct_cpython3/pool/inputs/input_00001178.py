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
    return max([a, b])


# Return the smallest of two arguments.
min2 = lambda x, y: x if x <= y else y

# A decorator is a function that takes another function as an argument, add some functionality and returns it back.
@functools.cache
def fibonacci(n: int):
    """
    Calculate the nth Fibonacci number using recursion.

    Args:
        n (int): The index of the Fibonacci number to compute.

    Returns:
        int: The nth Fibonacci number.
    """

    if n < 1:
        raise ValueError("Fibonacci number cannot be negative or zero.")
    elif n == 1:
        return 0
    elif n == 2:
        return 1
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)


def primes():
    """
    Generate an infinite sequence of prime numbers using the Sieve of Eratosthenes algorithm.

    Yields:
        int: The next prime number.
    """
    d = {}
    q = 2

    while True:
        if q not in d:
            yield q
            d[q * q] = [q]
        else:
            for p in d[q]:
                d.setdefault(p + q, []).append(p)
            del d[q]

        q += 1


if __name__ == '__main__':
    print(
        f'gcd(48, 18)={gcd(48, 18)}',
        f'min2(6, 7)={min2(6, 7)}',
        sep='\n'
    )

    print(f'fibonacci(5)={fibonacci(5)}')

    numbers = [1, 2, 3, 4, 5]
    squared_numbers = list(map(lambda x: x ** 2, numbers))
    squares = map(lambda x: x ** 2, numbers)

    def double(x):
        return x * 2

    doubles = map(double, numbers)

    squared = [number ** 2 for number in numbers]
    doubled = [lambda x: x * 2(number) for number in numbers]


# Use the generator from the previous seed to calculate prime numbers.
prime_generator = primes()