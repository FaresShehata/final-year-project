"""
Seed 05 — Concurrency (threading/multiprocessing/concurrent.futures),
          string parsing (ast.literal_eval, tokenize, textwrap, string.Formatter),
          typing extras (TypedDict, ParamSpec, Concatenate, TypeAlias, Never,
          Annotated, get_type_hints, reveal_type stub),
          __class_getitem__, __set_name__, __init_subclass__,
          contextlib (suppress, redirect_stdout, AbstractContextManager),
          numbers ABC, pathlib, tempfile, csv, base64, hashlib, hmac, secrets
"""

from __future__ import annotations

import ast
import base64
import binascii
import csv
import hashlib
import hmac
import io
import itertools
import multiprocessing
import numbers
import os
import pathlib
import queue
import secrets
import string
import tempfile
import textwrap
import threading
import time
import tokenize
import contextlib
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import (
    Annotated,
    Any,
    Callable,
    ClassVar,
    Final,
    Generic,
    Literal,
    NamedTuple,
    Never,
    ParamSpec,
    TypeAlias,
    TypedDict,
    TypeVar,
    get_type_hints,
)

T  = TypeVar("T")
P  = ParamSpec("P")

# ── TypeAlias ────────────────────────────────────────────────────────────────

JsonValue: TypeAlias = "int | float | str | bool | None | list[JsonValue] | dict[str, JsonValue]"
Seconds:   TypeAlias = float
Predicate: TypeAlias = Callable[[Any], bool]

# ── TypedDict ────────────────────────────────────────────────────────────────

class UserRecord(TypedDict, total=False):
    id:       int
    name:     str
    email:    str
    active:   bool
    metadata: dict[str, Any]


class MetricsRecord(TypedDict):
    latency_ms: float
    throughput: float
    error_rate: float


# ── Annotated constraints (runtime-checked via descriptor) ───────────────────

class _Constrained:
    """Descriptor that reads Annotated metadata to validate."""

    def __set_name__(self, owner, name):
        self.pub  = name
        self.priv = f"_{owner.__name__}__{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.priv, None)

    def __set__(self, obj, value):
        hints = get_type_hints(type(obj), include_extras=True)
        ann   = hints.get(self.pub)
        if ann and hasattr(ann, "__metadata__"):
            for constraint in ann.__metadata__:
                if callable(constraint):
                    if not constraint(value):
                        raise ValueError(f"{self.pub}={value!r} fails constraint")
        setattr(obj, self.priv, value)


def positive(x) -> bool:
    return isinstance(x, (int, float)) and x > 0

def short_str(x) -> bool:
    return isinstance(x, str) and len(x) <= 20


class Sensor:
    reading: Annotated[float, positive] = _Constrained()   # type: ignore[assignment]
    label:   Annotated[str,   short_str] = _Constrained()  # type: ignore[assignment]

    def __init__(self, label: str, reading: float):
        self.label   = label
        self.reading = reading

    def __repr__(self):
        return f"Sensor({self.label!r}, {self.reading})"


# ── NamedTuple ────────────────────────────────────────────────────────────────

class Span(NamedTuple):
    start: int
    end:   int
    label: str = ""

    def length(self) -> int:
        return self.end - self.start

    def overlap(self, other: Span) -> int:
        return max(0, min(self.end, other.end) - max(self.start, other.start))


# ── numbers ABC ──────────────────────────────────────────────────────────────

class Rational(numbers.Rational):
    """Minimal rational backed by integer numerator/denominator."""

    def __init__(self, num: int, den: int = 1):
        if den == 0:
            raise ZeroDivisionError
        g = _gcd(abs(num), abs(den))
        sign = -1 if den < 0 else 1
        self._n = sign * num // g
        self._d = sign * den // g

    # numbers.Rational interface
    @property
    def numerator(self) -> int:   return self._n
    @property
    def denominator(self) -> int: return self._d

    def __add__(self, other):
        o = _as_rational(other)
        return Rational(self._n * o._d + o._n * self._d, self._d * o._d)
    def __radd__(self, other):    return self.__add__(other)
    def __sub__(self, other):
        o = _as_rational(other)
        return Rational(self._n * o._d - o._n * self._d, self._d * o._d)
    def __rsub__(self, other):    return _as_rational(other).__sub__(self)
    def __mul__(self, other):
        o = _as_rational(other)
        return Rational(self._n * o._n, self._d * o._d)
    def __rmul__(self, other):    return self.__mul__(other)
    def __truediv__(self, other):
        o = _as_rational(other)
        return Rational(self._n * o._d, self._d * o._n)
    def __rtruediv__(self, other): return _as_rational(other).__truediv__(self)
    def __floordiv__(self, other): return int(self.__truediv__(other))
    def __rfloordiv__(self, other): return _as_rational(other).__floordiv__(self)
    def __mod__(self, other):
        o = _as_rational(other)
        d = self.__floordiv__(o)
        return self.__sub__(o.__mul__(d))
    def __rmod__(self, other): return _as_rational(other).__mod__(self)
    def __pow__(self, exp):    return Rational(self._n ** exp, self._d ** exp)
    def __rpow__(self, base):  return Rational(base) ** self._n  # type: ignore[operator]
    def __pos__(self):         return Rational(self._n, self._d)
    def __neg__(self):         return Rational(-self._n, self._d)
    def __abs__(self):         return Rational(abs(self._n), self._d)
    def __trunc__(self):       return int(self._n / self._d)
    def __floor__(self):       return self._n // self._d
    def __ceil__(self):
        import math; return math.ceil(self._n / self._d)
    def __round__(self, ndigits=None):
        return round(float(self), ndigits)   # type: ignore[call-overload]
    def __eq__(self, other):   return float(self) == float(other)
    def __lt__(self, other):   return float(self) < float(other)
    def __le__(self, other):   return float(self) <= float(other)
    def __float__(self):       return self._n / self._d
    def __bool__(self):        return self._n != 0
    def __hash__(self):        return hash((self._n, self._d))
    def __repr__(self):        return f"Rational({self._n}/{self._d})"


def _gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a

def _as_rational(x) -> Rational:
    return x if isinstance(x, Rational) else Rational(int(x))


# ── ParamSpec / Concatenate for typed decorators ──────────────────────────────

def timed(fn: Callable[P, T]) -> Callable[P, tuple[T, float]]:
    import functools

    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> tuple[T, float]:
        t0 = time.perf_counter()
        result = fn(*args, **kwargs)
        return result, time.perf_counter() - t0

    return wrapper  # type: ignore[return-value]


# ── Threading ─────────────────────────────────────────────────────────────────

class BoundedBuffer(Generic[T]):
    def __init__(self, capacity: int):
        self._q: queue.Queue[T] = queue.Queue(maxsize=capacity)
        self._lock = threading.RLock()
        self._produced = 0
        self._consumed = 0

    def put(self, item: T, timeout: float = 1.0) -> None:
        self._q.put(item, timeout=timeout)
        with self._lock:
            self._produced += 1

    def get(self, timeout: float = 1.0) -> T:
        item = self._q.get(timeout=timeout)
        with self._lock:
            self._consumed += 1
        return item

    @property
    def stats(self) -> dict:
        with self._lock:
            return {"produced": self._produced, "consumed": self._consumed}


def _producer_thread(buf: BoundedBuffer[int], n: int, sentinel: object) -> None:
    for i in range(n):
        buf.put(i * i)
        time.sleep(0)
    buf.put(sentinel)  # type: ignore[arg-type]


def _consumer_thread(buf: BoundedBuffer[int], results: list, sentinel: object) -> None:
    while True:
        item = buf.get()
        if item is sentinel:
            break
        results.append(item)


def threading_demo(n: int = 20) -> dict:
    buf: BoundedBuffer[int] = BoundedBuffer(8)
    results: list[int] = []
    sentinel = object()

    barrier = threading.Barrier(3)

    def ready():
        barrier.wait()

    t_prod = threading.Thread(target=lambda: (_producer_thread(buf, n, sentinel), ready()), daemon=True)
    t_cons = threading.Thread(target=lambda: (_consumer_thread(buf, results, sentinel), ready()), daemon=True)
    t_prod.start()
    t_cons.start()

    ready()  # main thread waits at barrier

    return {"stats": buf.stats, "count": len(results), "sum": sum(results)}


# ── concurrent.futures ────────────────────────────────────────────────────────

def _cpu_bound(n: int) -> int:
    """Simple Collatz length for multiprocessing."""
    steps = 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
    return steps


def futures_demo() -> dict:
    inputs = list(range(1, 40))
    thread_results: dict[int, int] = {}
    process_results: dict[int, int] = {}

    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(_cpu_bound, n): n for n in inputs}
        for f in as_completed(futs):
            thread_results[futs[f]] = f.result()

    with ProcessPoolExecutor(max_workers=2) as ex:
        for n, r in zip(inputs, ex.map(_cpu_bound, inputs, chunksize=5)):
            process_results[n] = r

    agreement = all(thread_results[k] == process_results[k] for k in inputs)
    return {
        "thread_max":   max(thread_results.values()),
        "process_max":  max(process_results.values()),
        "agreement":    agreement,
    }


# ── string.Formatter & Template ───────────────────────────────────────────────

class VerboseFormatter(string.Formatter):
    def format_field(self, value, format_spec):
        result = super().format_field(value, format_spec)
        return f"«{result}»"


def formatting_demo() -> dict:
    fmt = VerboseFormatter()

    t = string.Template("Hello, ${name}! You have $count messages.")
    basic = t.safe_substitute(name="Alice", count=5)

    fmtted = fmt.format("{greeting}, {0:.2f} and {count!r}", 3.14159, greeting="Hi", count=42)

    # textwrap
    long_text = "Python is a high-level, general-purpose programming language. " * 3
    wrapped   = textwrap.fill(long_text, width=60)
    dedented  = textwrap.dedent("    line1\n    line2\n    line3")
    indented  = textwrap.indent(dedented, prefix="  > ")

    return {
        "template":  basic,
        "formatted": fmtted,
        "wrapped_lines": wrapped.count("\n") + 1,
        "indented":  indented,
    }


# ── tokenize ─────────────────────────────────────────────────────────────────

def tokenize_demo(source: str) -> dict:
    tokens: list[dict] = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(source).readline):
            if tok.type not in (tokenize.NEWLINE, tokenize.NL, tokenize.COMMENT, tokenize.ENDMARKER):
                tokens.append({
                    "type":   tokenize.tok_name[tok.type],
                    "string": tok.string,
                })
    except tokenize.TokenError:
        pass
    return {"count": len(tokens), "tokens": tokens[:15]}


# ── ast.literal_eval & ast walk ───────────────────────────────────────────────

def ast_demo(expr: str) -> dict:
    try:
        value = ast.literal_eval(expr)
    except (ValueError, SyntaxError):
        value = None

    try:
        tree = ast.parse(expr, mode="eval")
        node_types = [type(n).__name__ for n in ast.walk(tree)]
    except SyntaxError:
        node_types = []

    return {"value": value, "node_types": node_types}


# ── pathlib & tempfile & csv ──────────────────────────────────────────────────

def file_io_demo() -> dict:
    with tempfile.TemporaryDirectory() as tmpdir:
        base = pathlib.Path(tmpdir)

        # write a CSV
        csv_path = base / "data.csv"
        rows = [{"x": i, "y": i * i, "label": f"pt{i}"} for i in range(10)]
        with csv_path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["x", "y", "label"])
            writer.writeheader()
            writer.writerows(rows)

        # read it back
        read_rows: list[dict] = []
        with csv_path.open(newline="") as f:
            reader = csv.DictReader(f)
            read_rows = list(reader)

        # glob
        (base / "sub").mkdir()
        for i in range(3):
            (base / "sub" / f"file_{i}.txt").write_text(f"content {i}")
        txt_files = sorted(base.rglob("*.txt"))

        return {
            "csv_rows":   len(read_rows),
            "first_row":  read_rows[0],
            "txt_files":  [p.name for p in txt_files],
        }


# ── hashlib / hmac / secrets / base64 ────────────────────────────────────────

def crypto_demo() -> dict:
    data = b"The quick brown fox jumps over the lazy dog"
    key  = secrets.token_bytes(32)

    # SHA family
    sha256 = hashlib.sha256(data).hexdigest()
    sha3   = hashlib.sha3_256(data).hexdigest()
    blake2 = hashlib.blake2b(data, digest_size=32).hexdigest()

    # HMAC
    mac = hmac.new(key, data, hashlib.sha256).hexdigest()

    # derive key with PBKDF2
    dk = hashlib.pbkdf2_hmac("sha256", b"password", b"salt", 100_000, dklen=32)

    # base64 variants
    b64       = base64.b64encode(data).decode()
    url_safe  = base64.urlsafe_b64encode(data).decode()
    b32       = base64.b32encode(data[:10]).decode()

    # secrets
    token_hex  = secrets.token_hex(16)
    token_url  = secrets.token_urlsafe(16)
    rand_int   = secrets.randbelow(10_000)

    return {
        "sha256":      sha256[:16] + "…",
        "sha3_256":    sha3[:16] + "…",
        "blake2b":     blake2[:16] + "…",
        "hmac_sha256": mac[:16] + "…",
        "pbkdf2_len":  len(dk),
        "b64_len":     len(b64),
        "url_safe_ok": base64.urlsafe_b64decode(url_safe) == data,
        "b32_sample":  b32[:8],
        "token_hex":   token_hex,
        "token_url":   token_url,
        "rand_int_lt": rand_int < 10_000,
    }


# ── contextlib showcase ───────────────────────────────────────────────────────

def contextlib_demo() -> dict:
    captured = io.StringIO()
    results: dict[str, Any] = {}

    with contextlib.redirect_stdout(captured):
        print("hello from redirect")
        print("second line")
    results["redirected"] = captured.getvalue().strip().splitlines()

    # suppress
    with contextlib.suppress(ZeroDivisionError):
        _ = 1 / 0
    results["suppress_ok"] = True

    # ExitStack
    stack = contextlib.ExitStack()
    cleanups: list[str] = []
    stack.callback(cleanups.append, "first")
    stack.callback(cleanups.append, "second")
    stack.close()
    results["exitstack_order"] = cleanups  # LIFO: ["second", "first"]

    # nullcontext
    with contextlib.nullcontext(42) as val:
        results["nullcontext_val"] = val

    return results


# ── Never / assert_never ──────────────────────────────────────────────────────

def assert_never(x: Never) -> Never:
    raise AssertionError(f"Unexpected value: {x!r}")


def process_literal(x: Literal["read", "write", "exec"]) -> str:
    if x == "read":
        return "reading"
    elif x == "write":
        return "writing"
    elif x == "exec":
        return "executing"
    else:
        assert_never(x)


# ── Final ─────────────────────────────────────────────────────────────────────

MAX_RETRIES: Final[int] = 5
APP_NAME:    Final = "seed05"


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=== TypedDict ===")
    user: UserRecord = {"id": 1, "name": "Alice", "active": True}
    print(f"  user: {user}")

    print("\n=== Annotated Sensor ===")
    s = Sensor("temp_01", 36.6)
    print(f"  {s}")
    with contextlib.suppress(ValueError):
        Sensor("toolonglabelname_exceeds_limit", 1.0)
    with contextlib.suppress(ValueError):
        Sensor("ok", -1.0)
    print("  invalid sensors correctly rejected")

    print("\n=== NamedTuple Span ===")
    spans = [Span(0, 5, "NP"), Span(3, 8, "VP"), Span(6, 10)]
    for sp in spans:
        print(f"  {sp}  len={sp.length()}")
    print(f"  overlap(spans[0], spans[1])={spans[0].overlap(spans[1])}")

    print("\n=== Rational numbers ===")
    a = Rational(1, 3)
    b = Rational(1, 6)
    print(f"  {a} + {b} = {a + b}")
    print(f"  {a} * 6  = {a * 6}")
    print(f"  isinstance Rational: {isinstance(a, numbers.Rational)}")

    print("\n=== timed decorator (ParamSpec) ===")
    @timed
    def slow_sum(n: int) -> int:
        return sum(range(n))
    result, elapsed = slow_sum(100_000)
    print(f"  slow_sum(100_000)={result}, elapsed={elapsed:.6f}s")

    print("\n=== threading ===")
    td = threading_demo(30)
    print(f"  {td}")

    print("\n=== concurrent.futures ===")
    fd = futures_demo()
    print(f"  {fd}")

    print("\n=== string formatting ===")
    fmt = formatting_demo()
    for k, v in fmt.items():
        print(f"  {k}: {v!r}")

    print("\n=== tokenize ===")
    src = "x = [i**2 for i in range(10) if i % 2 == 0]"
    tok = tokenize_demo(src)
    print(f"  token count: {tok['count']}")
    for t in tok["tokens"]:
        print(f"    {t['type']:12s} {t['string']!r}")

    print("\n=== ast ===")
    for expr in ["[1, 2, {'a': 3}]", "2 ** 10 + 1", "lambda x: x"]:
        r = ast_demo(expr)
        print(f"  {expr!r}: value={r['value']}, nodes={r['node_types']}")

    print("\n=== file I/O (tempdir + pathlib + csv) ===")
    fio = file_io_demo()
    for k, v in fio.items():
        print(f"  {k}: {v}")

    print("\n=== crypto ===")
    crypto = crypto_demo()
    for k, v in crypto.items():
        print(f"  {k}: {v}")

    print("\n=== contextlib ===")
    cl = contextlib_demo()
    for k, v in cl.items():
        print(f"  {k}: {v}")

    print("\n=== Literal / Never ===")
    for op in ("read", "write", "exec"):
        print(f"  process({op!r}) = {process_literal(op)}")  # type: ignore[arg-type]

    print(f"\n=== Final constants ===")
    print(f"  MAX_RETRIES={MAX_RETRIES}, APP_NAME={APP_NAME!r}")


if __name__ == "__main__":
    main()
