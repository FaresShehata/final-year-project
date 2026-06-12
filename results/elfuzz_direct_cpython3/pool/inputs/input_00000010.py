"""
Seed 03 — Functional programming: closures, higher-order functions, comprehensions,
          generators, coroutines (send/throw/close), itertools, functools,
          lambda calculus encoding, currying, partial application, trampolining
"""
import time


def test_closures():
    """
    Closures allow to create function objects that are 'bound' to the outer scope of a function.
    """

    def make_adder(x):
        """ Returns an adder from x """
        def add_y(y):
            return y + x

        return add_y

    # Closure is bound to the outer scope:
    add_5 = make_adder(5)
    print(add_5.__closure__)
    print(add_5(10))

    # Closures do not copy variables from their enclosing scopes:
    def closure_example():
        x = 42
        y = "test"
        z = None
        return x, y, z

    _, _, _ = closure_example()
    # print(x)  # NameError: name 'x' is not defined
    # print(y)  # NameError: name 'y' is not defined
    # print(z)  # NameError: name 'z' is not defined

# test_closures()


def test_higher_order_functions():
    """
    Higher-order function is a function that takes a function as argument or returns a function.
    These include map(), filter() and reduce().
    """

    def multiply_by_two(n):
        return n * 2

    l = [2, 3, 4]
    result = list(map(multiply_by_two, l))
    print(result)

# test_higher_order_functions()


def test_comprehensions_and_generators():
    """ Comprehension and generator expressions in Python can be used to create lists, sets or dictionaries. """

    # List comprehension with iterator expression:
    l = [i for i in range(5)]
    print(l)

    # List comprehension with conditional statement:
    l = [i for i in range(5) if i > 2]
    print(l)

    # Set comprehension:
    s = {i for i in range(5)}
    print(s)

    # Dictionary comprehension:
    d = {i: i**2 for i in range(5)}
    print(d)

# test_comprehensions_and_generators()


def test_coroutine_send_throw_close():
    """
    Coroutines enable communication between asynchronous processes by allowing them to send values from one process
    to another using the send() method.
    """
    import asyncio

    async def mycoroutine():
        while True:
            msg = await asyncio.wait_for(async