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

    # Generator expression with iterator expression:
    g = (i for i in range(5))
    print(g)

    # Set comprehension with iterator expression:
    s = {i for i in range(5)}
    print(s)

    # Dictionary comprehension with key/value expressions:
    d = {i: i ** 2 for i in range(5)}
    print(d)

# test_comprehensions_and_generators()


def test_coroutine_send_throw_close():
    """ Coroutines are similar to iterators but have a send method which allows you to pass values into them. """
    import inspect

    async def counter(start=0):
        count = start
        while True:
            count += 1
            yield count
            await time.sleep(.1)

    # Create coroutine object:
    c = counter()

    # Get next value returned by coroutine object:
    v = next(c)
    print(v)

    # Send 10 into the coroutine object:
    c.send(10)

    # Close the coroutine:
    c.close()

    try:
        c.send(None)
    except StopIteration:
        print('Coroutine has been closed.')
    else:
        assert False, 'Should raise StopIteration exception'

# test_coroutine_send_throw_close()


def test_itertools():
    """ Itertools module provides various functions that work on iterators to produce complex iterators. """

    import itertools

    # Infinite cycle through elements of iterable:
    l = ['a', 'b', 'c']
    it = iter(itertools.cycle(l))
    print(next(it))
    print(next(it))
    print(next(it))
    print(next(it))
    print(next(it))

    # Count and repeat functions:
    print(list(itertools.count()))
    print(list(itertools.repeat("foo", 3)))

    # Chain and zip functions:
    print(list(itertools.chain([1, 2], [3, 4])))
    print(list(itertools.zip_longest('abc', 'xyz')))
    print(list(zip(range(6), range(7))))

    # Islice and takewhile functions:
    print(list(itertools.islice(range(8), 3)))
    print(list(itertools.takewhile(lambda x: x < 5, range(10))))
    print(list(itertools.dropwhile(lambda x: x > 2, range(10))))

    # Filterfalse example:
    print(list(filter(lambda x: x >