"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

import asyncio

from functools import partial


async def simple_coroutine():
    print("Hello")
    await asyncio.sleep(3)
    print("World")
    return "done"


def decorator(func):
    """Decorator to log the name of a function"""

    def wrapper(*args, **kwargs):
        func_name = func.__name__
        args_str = ", ".join(f"{arg}" for arg in args) if args else ""
        kwargs_str = ", ".join(
            f"{key}={value}"
            for key, value in sorted(kwargs.items())
            if value is not None
        )
        result = func(*args, **kwargs)

        if isinstance(result, type(None)):
            result = ""

        print(f"Function {func_name}{f'({args_str}, {kwargs_str})':>5}: "
              f"returning {result}")

        return result

    return wrapper


@decorator
async def coroutine_with_args(arg1: str | int, arg2: str | int):
    """
    Coroutine that takes two arguments and returns their sum.
    """

    # TODO - add docstring with example usage
    return arg1 + arg2


class A:
    pass


class B(A):
    pass


# No need to write this again as it's only used once here
def print_type(obj, var_name=None):
    var_name = var_name or obj
    print(f"{var_name} has type '{type(obj).__name__}'")


print_type(None)
print_type(True)
print_type(False)
print_type(4.2)
print_type(-9876543210)
print_type(B())
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