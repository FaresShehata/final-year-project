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
    """Return the n-th Fibonacci number."""
    if n == 1 or n == 2:
        result = 1
    elif n % 2 == 0:
        result = fibonacci(n // 2) ** 2
    else:
        result = fibonacci((n - 1) // 2 + 1) * fibonacci((n - 1) // 2)
    return result


# A recursive example with memoization.
@functools.lru_cache(maxsize=None)
def fib(n: int):
    """
    Calculate the n-th Fibonacci number using recursion.

    :param n: The index of the Fibonacci number to be calculated.
    :return: The n-th Fibonacci number.
    """
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n-1) + fib(n-2)


# A simple integer counter that increments each time the function is called.
count = 0


def increment_count():
    global count
    count += 1
    return count


increment_count()


# Check whether the given number is a prime number.
def is_prime(x: int):
    """
    Determine whether the given number is a prime number.

    :param x: The number to check.
    :return: True if the number is prime, False otherwise.
    """
    if x < 2:
        return False
    if x == 2:
        return True
    if x % 2 == 0:
        return False
    i = 3
    while i * i <= x:
        if x % i == 0:
            return False
        i += 2
    return True


# Get all prime numbers up to a given limit.
def primes(limit=10_000):
    """
    Generate prime numbers up to a given limit.

    :param limit: The upper limit for generating prime numbers.
    :yield: Prime numbers less than or equal to the limit.
    """
    yield 2
    for num in range(3, limit+1, 2):
        if is_prime(num):
            yield num


# Create a list comprehension for squares of even numbers between 1 and 10.
squares_of_evens = [x**2 for x in range(1, 11) if x%2==0]

# Create a map object with square values of even numbers between 1 and 10.
square_map = list(map(lambda x: x*2, [1, 4, 5]))


# Multiply every element in the list `numbers` by 2.
[lambda x: x * 2(number) for number in numbers]


# Use the generator from the previous seed to calculate prime numbers.
prime_generator = primes()