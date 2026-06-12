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


# Print out the current value of the counter.
increment_count()


# Use list comprehension to create a new list containing only elements that pass a certain condition.

# Multiply every element in the list `numbers` by 2.
[lambda x: x * 2(number) for number in numbers]


# Use the generator from the previous seed to calculate prime numbers.
prime_generator = primes()