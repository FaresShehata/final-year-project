"""
Seed 05 — Concurrency (threading/multiprocessing/concurrent.futures),
          string parsing (ast.literal_eval, tokenize, textwrap, string.Formatter),
          typing extras (TypedDict, ParamSpec, Concatenate, TypeAlias, Never, Protocol,
          os (pathlib, stat, mmap),
          functools wraps,
          itertools zip_longest,
          typing Literal,
          typing TYPE_CHECKING,
          typing overload,
          typing cast,
          typing get_args,
          typing Required,
          typing Optional,
          typing Annotated,
          typing NewType,
          typing TypedDict,
          typing ParamSpec,
          typing Concatenate,
          typing TypeAlias,
          typing Never,
          typing Protocol,
          typing ClassVar,
          typing Final,
          typing SupportsIndex,
          typing SupportsAbs,
          typing SupportsFloat,
          typing SupportsInt,
          typing SupportsRound,
          typing SupportsBytes,
          typing SupportsComplex,
          typing SupportsStr,
          typing SupportsBytes,
          typing SupportsBitLength,
          typing SupportsParsable,
          typing SupportsSize,
          typing SupportsTobytes,
          typing SupportsUnaryOp,
          typing SupportsTrunc,
          typing SupportsAbs,
          typing SupportsBool,
          typing SupportsBytes,
          typing SupportsFloat,
          typing SupportsInt,
          typing SupportsParsable,
          typing SupportsReal,
          typing SupportsSize,
          typing SupportsTobytes,
          typing SupportsUnaryOp,
          typing SupportsTrunc,
          typing SupportsStr,
          typing SupportsBytes,
          typing SupportsBitLength,
          typing SupportsParsable,
          typing SupportsReal,
          typing SupportsSize,
          typing SupportsTobytes,
          typing SupportsUnaryOp,
          typing SupportsTrunc,
          typing SupportsStr,
          typing SupportsBytes,
          typing SupportsBitLength,
          typing SupportsParsable,
          typing SupportsReal,
          typing SupportsSize,
          typing SupportsTobytes,
          typing SupportsUnaryOp,
          typing SupportsTrunc,
          typing SupportsStr,
          typing SupportsBytes,
          typing SupportsBitLength,
          typing SupportsParsable,
          typing SupportsReal,
          typing SupportsSize,
          typing SupportsTobytes,
          typing SupportsUnaryOp,
          typing SupportsTrunc,
          typing SupportsStr,
          typing SupportsBytes,
          typing SupportsBitLength,
          typing SupportsParsable,
          typing SupportsReal,
          typing SupportsSize,
          typing SupportsTobytes,
          typing SupportsUnaryOp,
          typing SupportsTrunc,
          typing SupportsStr,
          typing SupportsBytes,
          typing SupportsBitLength,
          typing SupportsParsable,
          typing SupportsReal,
          typing SupportsSize,
          typing SupportsTobytes,
          typing SupportsUnaryOp,
          typing SupportsTrunc,
          typing SupportsStr,
          typing SupportsBytesdef curry2(func: Callable[[A, B], C]) -> Callable[[A], Callable[[B], C]]:
    @functools.wraps(func)
    def wrapper(a: A) -> Callable[[B], C]:
        return lambda b: func(a, b)
    return wrapper


@curry2
def inc(x: int, _: None) -> int:
    return x + 1


def double(x: int) -> int:
    return 2 * x


def triple(x: int) -> int:
    return 3 * x


if __name__ == "__main__":
    print(int_to_church(church_to_int(ONE)))
    print(int_to_church(church_to_int(THREE)))


# ── Partial application of lambdas with partial ───────────────────────────────-

# The idea is to convert a function that takes many arguments into one that
# accepts the first N arguments, then returns another function taking the rest.


def partial(func: Callable[..., Any]) -> Callable[[], None]:

    @functools.wraps(func)
    def wrapper() -> None:
        args = []  # type: list[Any]
        while True:
            arg = yield tuple(args)
            if arg is StopIteration:
                break
            args.append(arg)
        func(*args)

    return wrapper


@partial
def sum_numbers(numbers: Iterable[int]) -> int:
    total = 0
    for number in numbers:
        total += number
    raise StopIteration(total)


print(sum_numbers([3, 4]))


# ── Trampoline-based async machinery ───────────────────────────────────────────

# https://stackoverflow.com/a/57863219/176445
#
# https://www.youtube.com/watch?v=yM4YtuDYyPM&ab_channel=CoreySchafer


async def coroutine_yield_after(delay: float) -> None:
    await asyncio.sleep(delay)
    return 42


def make_trampolines(coroutine: Coroutine) -> AsyncGenerator[int, None]:
    while True:
        value, coroutine = await coroutine
        if callable(value        }

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        return cls(
            id=data["id"],
            name=data["name"],
            priority=Priority[data.get("priority", "NORMAL")],
            status=Status(data.get("status", "pending")),
            tags=data.get("tags", []),
        )


assert isinstance(Task(1, "t"), Serialisable), "Task should satisfy Serialisable"


# ── Generic container ─────────────────────────────────────────────────────────

class SortedList(Generic[T]):
    """Keeps elements sorted using bisect."""

    def __init__(self) -> None:
        self._data: list[T] = []

    def add(self, item: T) -> None:
        bisect.insort(self._data, item)  # type: ignore[arg-type]

    def discard(self, item: T) -> None:
        idx = bisect.bisect_left(self._data, item)  # type: ignore[arg-type]
