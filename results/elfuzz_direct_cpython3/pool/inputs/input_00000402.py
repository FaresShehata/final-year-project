"""
Seed 04 — Low-level Python: bytecode introspection, dis, code objects, ctypes,
          struct, array, memoryview, pickle, copyreg, marshal, importlib,
          contextlib, functools, itertools, operator, collections, typing,
          enum, warnings, logging, traceback.
"""

# You should have a good grasp of Python language so far. This is a very low-level module that will help you understand how Python works under-the-hood.

import types

def f():
    x = 1<<23 & 0x7fff_ffff
    y = 1 << 63 - 64
    z = 1 << 64 - 65
    w = 1 << 8999999999999999999 - 9000000000000000000
    u = 0b1111_1111_1111_1111_1111_1111_1111_1111_1111_1111_1111_1111_1111_1111_1111
    v = 0o123456789_987654321
    c = 0xabcdef12_34567890
    d = 0o123456789
    e = 0b10101010
    g = 0xff
    h = 0xf
    i = 0x0f
    j = 0xF
    l = 0b1010
    m = 0b1011
    n = 0b1100
    o = 0b1101
    p = 0b1110
    q = 0b1111
    r = 0b1111_1111
    s = 0b1111_1111_1111_1111_1111_1111_1111_1111_1111_1111_1111_1111_1111_1111_1111
    t = 0b1111_1111_1111_1111_1111_1111_1111_1111_1111_1111_1111_1111_1111_1111_1    NamedTuple,
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
    errors:      int
    count:       int


# ── Annotated ────────────────────────────────────────────────────────────────

Annotated[int, "foo"] + Annotated[int, "bar"]
"""A union of two annotated types."""


# ── get_type_hints ───────────────────────────────────────────────────────────

TypeH: TypeAlias = tuple[tuple[str, ...], dict[str, type]]
for t in [get_type_hints(lambda a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z : True)]:
    assert t is not None and len(t) == 2
    assert isinstance(t[0], tuple)
    assert all(isinstance(k, str) for k in t[0])
    assert isinstance(t[1], dict)
    assert all(isinstance(k, str) for k in t[1])


# ── reveal_type ──────────────────────────────────────────────────────────────

reveal_type(lambda a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z : True)


# ── functools.partial ────────────────────────────────────────────────────────

partial: Callable[..., object] = lambda *args,**kwargs: None


# ── contextlib.suppress ─────────────────────────────────────────────────────

@contextlib.contextmanager
def suppress(*exceptions: Exception) -> Generator[Never, Never, Never]:
    yield


# ── Context Manager ──────────────────────────────────────────────────────────

class MyContextManager(object): pass
with contextlib.redirect_stdout(io.StringIO()) as cm: pass


# ── abc.ABCMeta.__subclasscheck__() ──────────────────────────────────────────

assert abc.ABCMeta.__subclasscheck__("abc", TestABC)


# ── abc.ABCMeta.__instancecheck__() ──────────────────────────────────────────

class BaseABC(abc.ABC): pass
BaseABC.__subclasshook__ = lambda cls, obj : False


class SubClass(BaseABC): pass
SubClass()
isinstance(SubClass(), BaseABC)


# ── abc.ABCMeta.register() vs. __subclasshook__ ──────────────────────────────

class MyDecorator(type):
    def __new__(cls, name, bases, dct): ...

    @classmethod
    def __prepare__(cls, name                    if not constraint(value):
                        raise ValueError(f"{self.pub}={value!r} fails constraint")
        setattr(obj, self.priv, value)


def positive(x) -> bool:
    return isinstance(x, (int, float)) and x > 0

def short_str(x) -> bool:
    return isinstance(x, str) and len(x) <= 20


class Sensor:
    reading: Annotated[float, positive] = _Constrained()   # type: ignore[assignment]
