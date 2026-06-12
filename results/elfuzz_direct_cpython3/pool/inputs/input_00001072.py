"""
Seed 03 — Functional programming: closures, higher-order functions, comprehensions,
          generators, coroutines (send/throw/close), itertools, functools,
          lambda calculus encoding, currying, partial application, trampolining
"""

from __future__ import annotations

import functools
import itertools
import operator
import sys
from collections.abc import Callable, Generator, Iterable, Iterator
from typing import Any, TypeVar

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")

# ── Lambda-calculus church encodings ─────────────────────────────────────────

TRUE  = lambda t: lambda f: t
FALSE = lambda t: lambda f: f
IF    = lambda b: lambda t: lambda f: b(t)(f)
AND   = lambda p: lambda q: p(q)(p)
OR    = lambda p: lambda q: p(p)(q)
NOT   = lambda p: p(FALSE)(TRUE)

ZERO  = lambda f: lambda x: x
SUCC  = lambda n: lambda f: lambda x: f(n(f)(x))
ADD   = lambda m: lambda n: lambda f: lambda x: m(f)(n(f)(x))
MUL   = lambda m: lambda n: lambda f: n(m(f))
ONE   = SUCC(ZERO)
TWO   = SUCC(ONE)
THREE = SUCC(TWO)

def church_to_int(n) -> int:
    return n(lambda x: x + 1)(0)

def int_to_church(n: int):
    result = ZERO
    for _ in range(n):
        result = SUCC(result)
    return result


# ── Currying & partial application ───────────────────────────────────────────

def curry(fn: Callable) -> Callable:
    """Auto-curry a function based on its arity."""
    arity = fn.__code__.co_argcount

    @functools.wraps(fn)
    def curried(*args):
        if len(args) >= arity:
            return fn(*args[:arity])
        return lambda *more: curried(*(args + more))

    return curried


@curry
def add3(a: int, b: int, c: int) -> int:
    return a + b + c


@curry
def fold_str(sep: str, left: str, right: str) -> str:
    return f"{left}{sep}{right}"


def compose(*fns: Callable) -> Callable:
    """Right-to-left function composition."""
    def composed(x):
        for f in reversed(fns):
            x = f(x)
        return x
    return composed


def pipe(*fns: Callable) -> Callable:
    """Left-to-right pipeline."""
    def piped(x):
        for f in fns:
            x = f(x)
        return x
    return piped


add2 = add3(2)


# ── Partial application of curried functions ────────────────────────────────

def partial(fn: Callable, /, *args: Any) -> Callable:
    """Partial application of a curried function.

    We can't use functools.partial because it doesn't work with variadic arguments.
    """
    if args and not all(isinstance(arg, type(args[0])) for arg in args[1:]):
        raise TypeError("All arguments must be the same type.")
    elif isinstance(args[-1], Callable):
        return partial(args[-1], *(fn(*args[:-1])))
    else:
        return lambda *more_args: fn(*(args + more_args))


def first_three(xs: list[int]) -> tuple[int]:
    return xs[:3]


first_three_partial = partial(first_three)


# ── Trampoline pattern ─────────────────────────────────────────────────────

class StackUnderflow(Exception):
    pass


class StackOverrun(Exception):
    pass


def eval_tramp(
    stack: list[Any],
    fn: Callable[[list[Any]], tuple[list[Any], bool]],
) -> None:
    while True:
        try:
            head, tail = fn(stack)
            if not tail:
                raise StackUnderflow()
            stack.extend(head)
        except StackOverflow as e:
            raise e.with_traceback(sys.exc_info()[2])


def eval_closures(
    stack: list[tuple[list[Any], Callable]],
    fn: Callable[[tuple[list[Any], Callable]], tuple[list[Any], bool]],
) -> None:
    while True:
        try:
            head, tail = fn(tuple(reversed(stack)), lambda x, y: x[::-1] + y[::-1])
            if not tail:
                raise StackUnderflow()
            stack.append(head)
        except StackOverflow as e:
            raise e.with_traceback(sys.exc_info()[2])


def eval_closure_stack(
    func: Callable[..., Any],
    closure_vars: tuple,
    env: dict[str, Any],
    *,
    closure_size: int | None = None,
) -> Callable[..., Any]:
    """Evaluate a closure by restoring the environment at its creation time."""

    # TODO: this is just an implementation detail; we should have some way to
    #       extract the closure's variables from an AST node so that we don't need
    #       to reimplement this manually every time we want to evaluate them

    if closure_vars == ("self", "cls"):
        return func

    free_vars = frozenset(env.keys()).difference(closure_vars)
    env_copy = {k: v for k, v in env.items()}

    def new_env(func_globals: dict[str, Any]) -> dict[str, Any]:
        nonlocal env_copy  # noqa
        for var_name in free_vars:
            del env_copy[var_name]
        return env_copy

    def closure(*args):
        closure_size_ = closure_size or len(closure_vars)
        closure_env = {
            **{var_name: value for var_name, value in func_globals.items()},
            **env_copy,
        }
        closure_args = (*closure_vars, *args)
        return [
            [arg.value for arg in args][::-1][:closure_size_],
            closure_env,
        ]

    return closure


def test_eval_closure_stack():
    class Foo(object):

        def bar(self, a, b, c):
            print(a, b, c)
            return self.a + self.b + self.c

        def baz(self, d, e, f):
            print(d, e, f)
            return self.d + self.e + self.f

    foo = Foo()

    env = {"a": 2, "b": 3, "c": 5}
    result = eval_closure_stack(foo.bar, ("self", "cls"), env=env, closure_size=1    ([lambda _, y: y + 1], lambda x: lambda y: y + 1),
    ([lambda x, y: x + y], lambda x: lambda y: x + y),
    ([], lambda x: []),
    ([lambda