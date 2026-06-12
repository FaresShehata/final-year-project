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
    args_len, kwargs_len = len(signature(fn).parameters.values()), len(fn.__code__.co_varnames) - fn.__defaults__.index(None)
    if not args_len or args_len < kwargs_len:
        return fn
    return lambda *a, **kw: fn(*(list(a) + [v for k, v in kw.items()[:-kwargs_len]]))


def partial(func: Callable[[A], B], *a, **kwa):
    """Return a partial of func with the given arguments and keyword arguments."""
    return lambda *b, **kw: func(*(a + b), **{**dict(kwa), **kw})


curry(int_to_church)


# ── Trampoline & Tail-Recursive Functions ─────────────────────────────────────

def trampoline(f: Callable[..., Any]):
    """Wrap a function into a trampoline.

    A trampoline is an unrolling technique used to avoid stack overflow.
    """
    while callable(f):
        f = f()
    return f


trampoline(2 * 42)


# ── Coroutines & Asyncio ───────────────────────────────────────────────────────

async def coroutine(name: str) -> str:
    """A simple coroutine that prints its name and sleeps for 5 seconds."""
    print(name)
    await asyncio.sleep(5)
    return name


coroutine("Hello")


# ── Higher Order Functions ─────────────────────────────────────────────────────-

def curry_map(fn: Callable[[A], B], iterable: Iterable[A]) -> Iterator[B]:
    """Curries the map function over an iterator."""
    return map(fn, iterable)


def compose(*funcs: Callable[..., Any]) -> Callable[[Any], Any]:
    """Compose a series of functions."""
    return funclist.reduce(operator.methodcaller("__rshift__"), funcs[::-1])


compose(print, lambda x: x + 1)(1)


# ── Higher-Order Generators ───────────────────────────────────────────────────-

def take(iterable: Iterable[A], n: int = 1) -> Iterator[A]:
    return itertools.islice(iterable, n)


take((i for i in range(6)), 3)


def drop(iterable: Iterable[A], n: int = 1) -> Iterator[A]:
    """Drop the first n elements of an iterable."""
    iterator = iter(iterable)
    for _ in range(n):
        next(iterator)
    return iterator


drop((i for
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "priority": self.priority.name,
            "status": self.status.value,
            "tags": self.tags,
        },
    ), 3)

for tag in drop(drop({i for _, i in enumerate(range(6))}, 3)):
    print(tag)

assert list(map(lambda ch: ord(ch), "Hello")) == [
    ch for ch in "Hello"] == [
    ch for ch in {ch for ch in "Hello"}] == [
    ch for ch in [ord(ch) for ch in "Hello"]] == [
    ord(ch) for ch in "Hello"]

print(list(map(ord, drop({i for _, i in enumerate(range(6))}, 3))))

print("\u0394")  # U+0394 GREEK CAPITAL LETTER DELTA
print(chr(0x0394))

map(ord, chr(0x0394))

print("\N{GREEK CAPITAL LETTER DELTA}")

print("\U00000394")

chr(0x0394)

print(fr'\N{GREEK CAPITAL LETTER DELTA}')

print(chr(0x0394))

print('\N{GREEK CAPITAL LETTER DELTA}')


print('α')  # U+03B1 GREEK SMALL LETTER ALPHA
print('Α')
print('\u03B1')

print('β')  # U+03B2 GREEK CAPITAL LETTER Beta
print('Β')
print('\u03B2')


print(r'α\β\γ\δ\ε\ζ\η\θ\ι\κ\λ\μ\nν\ξ\xi\ο\π\ρ\rho\σ\ς\τ\t\υ\v\φ\phi\χ\chi\ψ\Psi\ω\Omega\omega')

print("This isn't a string.\tAnd this isn't either.")

print(_r'This isn\'t a raw string.')

print(repr("""\
One of these lines will be split up by whitespace!
Another one won't."""))

print(__doc__)

print('''As is the case with most strings, backslash (\) can be escaped 
with another backslash (\) if you want it treated literally.''')

print(r'''Raw strings don’t recognize escape sequences at all! So \n would actually appear literally.''')
print("asdasdasd\\ndadadsdad".split())


print("abc".center(7))
print("abc ".ljust(7))
print("abc ".rjust(7))

print("|{:import weakref
import weakref.remainder as remainder_wrt_weakref


class Test(unittest.TestCase):
    def test_five(self) -> None:
        """https://docs.python.org/3/library/dis.html#dis.dis"""
        a = "a"
        b = "b"
        c = "c"
        five = lambda x, y, z: x + y * z
        code = five.__code__
        assert isinstance(a, str) and isinstance(b, str) and isinstance(c, str)
        assert len(code.co_varnames) == 2
        assert len(code.co_names) == 1
        assert code.co_nlocals == 5
        assert code.co_stacksize == 8
        assert code.co_flags == 960
        assert code.co_firstlineno == 1
        assert code.co_lnotab == b"\x00\x01\x00" if six.PY2 else b""
        assert code.co_freevars == ()
        assert code.co_cellvars == ("y",)

    def test_code_objects(self) -> None:
        """http://python-history.blogspot.com/2013/08/complete-guide-to-code-object.html"""
        code = compile("Hello World!", "<string>", "exec")
        self.assertEqual(type(code), types.CodeType)
        self.assertEqual(len(inspect.getargspec(code).args), 1)
        self.assertEqual(code.co_consts[0], "Hello World!")

    def test_importlib(self) -> None:
        """https://docs.python.org/3/library/importlib.html"""
        spec = importlib.util.spec_from_file_location(
            "example_module", "/path/to/example_module.py",
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert hasattr(module, "function")
        assert isinstance(module.function, types.FunctionType)

    def test_sys_internals(self) -> None:
        """
        https://docs.python.org/3/c-api/intro.html#c.SYS_MAX_SIZE_T
        https://docs.python.org/3/c-api/memory.html#c.Py_ssize_t
        https://docs.python.org/3/c-api/object.html#c.PyObject
        """
        assert (sys.maxsize >> 32) >= 0xFFFFFFFF // 2
        assert sys.intern is getattr(sys, "_intern")

    def test_frame_inspection(self) -> None:
        """https://docs.python.org/3/reference/datamodel.html#the-standard-type-hierarchy"""
        # repr() of a Frame object contains the name of its type, which may be useful for debugging.
        class MyFrame(types.FrameType):
            pass
        f = MyFrame()
        print(f"{type(f)!r} {f}")
        assert f.f_back is None
        # The standard library module “inspect” provides functions to extract information from frames in various formats.
       