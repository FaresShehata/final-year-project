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


# ── Closures & factories ──────────────────────────────────────────────────────

def make_counter(start: int = 0, step: int = 1):
    state = [start]          # mutable cell avoids nonlocal for clarity

    def increment() -> int:
        v = state[0]
        state[0] += step
        return v

    def reset() -> None:
        state[0] = start

    def peek() -> int:
        return state[0]

    increment.reset = reset  # type: ignore[attr-defined]
    increment.peek  = peek   # type: ignore[attr-defined]
    return increment


def make_accumulator(init: float = 0.0) -> Callable[[float], float]:
    total = init

    def acc(x: float) -> float:
        nonlocal total
        total += x
        return total

    return acc


def memoize_rec(fn: Callable) -> Callable:
    """Memoisation decorator that handles recursive calls correctly."""
    cache: dict = {}

    @functools.wraps(fn)
    def wrapper(*args):
        if args not in cache:
            cache[args] = fn(*args)
        return cache[args]

    return wrapper


# ── Trampolining ──────────────────────────────────────────────────────────────

class Thunk:
    __slots__ = ("fn", "args")

    def __init__(self, fn, *args):
        self.fn = fn
        self.args = args


def trampoline(f) -> Callable:
    @functools.wraps(f)
    def wrapper(*args):
        result = f(*args)
        while isinstance(result, Thunk):
            result = result.fn(*result.args)
        return result
    return wrapper


def _even_tc(n: int, acc: bool) -> "bool | Thunk":
    if n == 0:
        return acc
    return Thunk(_odd_tc, n - 1, acc)


def _odd_tc(n: int, acc: bool) -> "bool | Thunk":
    if n == 0:
        return not acc
    return Thunk(_even_tc, n - 1, acc)


is_even_tc = trampoline(lambda n: Thunk(_even_tc, n, True))


# ── Generator coroutines (send / throw / close) ───────────────────────────────

def running_average() -> Generator[float, float, str]:
    """Coroutine: send values, receive running average."""
    total = 0.0
    count = 0
    value = yield 0.0          # prime
    while True:
        total += value
        count += 1
        try:
            value = yield total / count
        except GeneratorExit:
            return f"closed after {count} samples"


def pipeline_gen(source: Iterable[int]) -> Generator[str, None, None]:
    """Multi-stage generator pipeline."""
    # stage 1: filter evens
    evens = (x for x in source if x % 2 == 0)
    # stage 2: square
    squared = (x * x for x in evens)
    # stage 3: stringify with metadata
    for i, val in enumerate(squared):
        yield f"[{i:02d}] {val}"


# ── itertools showcase ────────────────────────────────────────────────────────

def itertools_showcase():
    results: dict[str, Any] = {}

    # combinations / permutations
    results["comb_3_2"]  = list(itertools.combinations(range(5), 2))
    results["perm_abc"]  = list(itertools.permutations("abc"))
    results["prod_2x3"]  = list(itertools.product([0, 1], repeat=3))

    # groupby
    data = sorted([("a", 1), ("b", 2), ("a", 3), ("b", 4), ("c", 5)], key=operator.itemgetter(0))
    groups = {k: list(v) for k, v in itertools.groupby(data, key=operator.itemgetter(0))}
    results["groupby"] = groups

    # chain, islice, cycle, repeat
    chained = list(itertools.islice(
        itertools.chain(itertools.repeat("X", 3), itertools.cycle("abc")),
        10,
    ))
    results["chain_islice_cycle"] = chained

    # accumulate
    results["cumsum"]  = list(itertools.accumulate(range(1, 8)))
    results["cumprod"] = list(itertools.accumulate(range(1, 7), operator.mul))

    # starmap
    results["starmap"] = list(itertools.starmap(pow, [(2, 3), (3, 2), (10, 0)]))

    # takewhile / dropwhile
    seq = [1, 2, 3, 4, 5, 4, 3]
    results["takewhile_lt4"] = list(itertools.takewhile(lambda x: x < 4, seq))
    results["dropwhile_lt4"] = list(itertools.dropwhile(lambda x: x < 4, seq))

    # compress
    mask = [1, 0, 1, 0, 1, 1, 0]
    results["compress"] = list(itertools.compress(seq, mask))

    # zip_longest
    results["zip_longest"] = list(itertools.zip_longest("abc", [1, 2], fillvalue="?"))

    # pairwise (3.10+)
    try:
        results["pairwise"] = list(itertools.pairwise(range(5)))
    except AttributeError:
        results["pairwise"] = "n/a (pre-3.10)"

    return results


# ── functools showcase ────────────────────────────────────────────────────────

def functools_showcase():
    results: dict[str, Any] = {}

    # partial
    double = functools.partial(operator.mul, 2)
    results["double"] = [double(x) for x in range(6)]

    # reduce
    results["factorial_10"] = functools.reduce(operator.mul, range(1, 11), 1)

    # lru_cache
    @functools.lru_cache(maxsize=128)
    def fib(n: int) -> int:
        return n if n < 2 else fib(n - 1) + fib(n - 2)

    results["fib_30"] = fib(30)
    results["fib_cache"] = fib.cache_info()

    # total_ordering
    @functools.total_ordering
    class Version:
        def __init__(self, major, minor, patch):
            self.v = (major, minor, patch)
        def __eq__(self, other):
            return self.v == other.v
        def __lt__(self, other):
            return self.v < other.v
        def __repr__(self):
            return "v" + ".".join(map(str, self.v))

    versions = [Version(1, 2, 0), Version(0, 9, 5), Version(1, 2, 1), Version(2, 0, 0)]
    results["versions_sorted"] = sorted(versions)

    # singledispatch
    @functools.singledispatch
    def process(value) -> str:
        return f"unknown({value!r})"

    @process.register(int)
    def _(value: int) -> str:
        return f"int:{value * 2}"

    @process.register(str)
    def _(value: str) -> str:
        return f"str:{value.upper()}"

    @process.register(list)
    def _(value: list) -> str:
        return f"list:{len(value)}"

    results["dispatch"] = [process(x) for x in [42, "hello", [1, 2, 3], 3.14]]

    # cached_property (functools)
    class Expensive:
        def __init__(self, data: list[int]):
            self.data = data
            self._calls = 0

        @functools.cached_property
        def processed(self) -> list[int]:
            self._calls += 1
            return sorted(set(self.data))

    e = Expensive([3, 1, 4, 1, 5, 9, 2, 6, 5])
    _ = e.processed
    _ = e.processed   # second access: should not recompute
    results["cached_property_calls"] = e._calls  # must be 1

    return results


# ── Comprehension showcase ────────────────────────────────────────────────────

def comprehension_showcase():
    # nested list comprehension (matrix transpose)
    matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    transpose = [[row[i] for row in matrix] for i in range(3)]

    # dict comprehension with conditional
    squares = {x: x * x for x in range(-5, 6) if x != 0}

    # set comprehension
    vowels_in = {c for word in ["hello", "world", "python"] for c in word if c in "aeiou"}

    # nested generator inside sum
    flat_sum = sum(x * y for x in range(1, 4) for y in range(1, 4) if x != y)

    # walrus in comprehension
    filtered = [y for x in range(20) if (y := x * x - 3 * x + 2) > 0 and y < 50]

    # dict from two lists via zip
    keys   = ["alpha", "beta", "gamma", "delta"]
    values = [10, 20, 30, 40]
    merged = {k: v for k, v in zip(keys, values)}

    return {
        "transpose": transpose,
        "squares": squares,
        "vowels": sorted(vowels_in),
        "flat_sum": flat_sum,
        "filtered": filtered,
        "merged": merged,
    }


# ── Infinite sequences ────────────────────────────────────────────────────────

def naturals(start: int = 0) -> Iterator[int]:
    n = start
    while True:
        yield n
        n += 1


def sieve(limit: int) -> list[int]:
    """Sieve of Eratosthenes using comprehension + bytearray."""
    if limit < 2:
        return []
    comp = bytearray([1]) * (limit + 1)
    comp[0] = comp[1] = 0
    for i in range(2, int(limit ** 0.5) + 1):
        if comp[i]:
            comp[i * i::i] = bytearray(len(comp[i * i::i]))
    return [i for i, v in enumerate(comp) if v]


def collatz(n: int) -> Generator[int, None, int]:
    """Yields Collatz sequence, returns number of steps."""
    steps = 0
    while n != 1:
        yield n
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
    yield 1
    return steps


# ── Y-combinator ─────────────────────────────────────────────────────────────

Y = lambda f: (lambda x: f(lambda *args: x(x)(*args)))(lambda x: f(lambda *args: x(x)(*args)))

fact_y = Y(lambda f: lambda n: 1 if n == 0 else n * f(n - 1))
fib_y  = Y(lambda f: lambda n: n if n < 2 else f(n - 1) + f(n - 2))


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=== Church numerals ===")
    five = ADD(TWO)(THREE)
    six  = MUL(TWO)(THREE)
    print(f"  2+3={church_to_int(five)}, 2*3={church_to_int(six)}")
    print(f"  NOT(TRUE)(1)(0)={NOT(TRUE)(1)(0)}")

    print("\n=== Curry / compose / pipe ===")
    add3_5 = add3(2)(3)
    print(f"  add3(2)(3)(5)={add3_5(5)}")
    transform = pipe(lambda x: x + 1, lambda x: x * 3, lambda x: x - 2)
    print(f"  pipe(+1, *3, -2)(4) = {transform(4)}")
    compose_r = compose(lambda x: x - 2, lambda x: x * 3, lambda x: x + 1)
    print(f"  compose(-2,*3,+1)(4) = {compose_r(4)}")

    print("\n=== Closures ===")
    cnt = make_counter(start=10, step=3)
    print(f"  counter: {[cnt() for _ in range(5)]}")
    cnt.reset()
    print(f"  after reset peek: {cnt.peek()}")
    acc = make_accumulator()
    print(f"  acc: {[acc(x) for x in [1, 2, 3, 4, 5]]}")

    print("\n=== Trampoline is_even ===")
    print(f"  is_even(1000)={is_even_tc(1000)}, is_even(999)={is_even_tc(999)}")

    print("\n=== Coroutine running_average ===")
    gen = running_average()
    next(gen)
    avgs = []
    for v in [10, 20, 30, 40, 50]:
        avgs.append(gen.send(float(v)))
    gen.close()
    print(f"  running avgs: {[round(a, 2) for a in avgs]}")

    print("\n=== Pipeline generator ===")
    for line in pipeline_gen(range(1, 20)):
        print(f"  {line}")

    print("\n=== itertools ===")
    it = itertools_showcase()
    for k, v in it.items():
        print(f"  {k}: {v}")

    print("\n=== functools ===")
    ft = functools_showcase()
    for k, v in ft.items():
        print(f"  {k}: {v}")

    print("\n=== Comprehensions ===")
    comp = comprehension_showcase()
    for k, v in comp.items():
        print(f"  {k}: {v}")

    print("\n=== Sieve ===")
    primes = sieve(80)
    print(f"  primes up to 80: {primes}")

    print("\n=== Collatz ===")
    for n in [6, 27]:
        seq = list(collatz(n))
        print(f"  collatz({n}): length={len(seq)}, max={max(seq)}")

    print("\n=== Y-combinator ===")
    print(f"  fact(10)={fact_y(10)}, fib(15)={fib_y(15)}")


if __name__ == "__main__":
    main()
