"""
Seed 01 — OOP, metaclasses, descriptors, decorators, context managers, generators
"""

# TODO: Check why I can't import from other files (using relative imports)
from .helpers import *
import random


class TestMeta(type):

    def __new__(cls, name, bases, body):
        cls_attr = {"test": lambda self, reason: setattr(self, "_test", reason)}
        for attr_name, value in body.items():
            if callable(value) and not attr_name.startswith("_"):
                cls_attr[attr_name] = value
        return type.__new__(cls, name, bases, dict(cls_attr))


class TestCase(metaclass=TestMeta):
    pass


class MyTestCase(TestCase):
    def test_something(self) -> None:
        assert False, "oh no!"


class AnotherTestCase(TestCase):
    def test_another(self) -> None:
        assert True


# ── Type Annotations ──────────────────────────────────────────────────────────



# ── Class Type ────────────────────────────────────────────────────────────────
#
# Source:
# https://stackoverflow.com/questions/67891505/python-operator-overloading-with-class-type
#

class OperatorOverloadable:
    """
    A class that supports operator overloading. The attribute `__operators` should be defined as a dictionary mapping
    operator symbols to their corresponding methods.

    Example:

    ```python
    class MyClass(OperatorOverloadable):
        def __init__(self, x: int):
            self.x = x

        def __add__(self, other: 'MyClass') -> 'MyClass':
            return MyClass(self.x + other.x)
    ```
    """

    __operators: Dict[str, Callable]

    @classmethod
    def apply_operator(cls, op_symbol: str, operands: List[Any], method_name: Optional[str] = None) -> Any:
        """
        Apply an operator on the given operands using the specified method or default method.

        Args:
            op_symbol (str): The operator symbol ('+', '-', '*', '/', etc.).
            operands (List[Any]): A list of operands.
            method_name (Optional[str], optional): The method to use for applying the operator. If None, it will be
                inferred from the operator symbol. Defaults to None.

        Returns:
            Any: The result of applying the operator on the given operands.

        Raises:
            KeyError: If the operator symbol does not have a corresponding method.
        """
        method = getattr(cls, method_name or f"_{op_symbol}_operator") \
            if hasattr(cls, method_name or f"_{op_symbol}_operator") else getattr(cls, f"_operator_{    last:     str
    gender:   Literal["M", "F"]
    email:    str | None
    ip_address: str | None
    joined:   Seconds

def user_record_to_str(record: UserRecord) -> str:
    return f"{record['id']} {record['first']}{record['last']:>10} {record.get('gender', ''):>3}"

# ── ParamSpec ────────────────────────────────────────────────────────────────

def log_each(f: Callable[P, T]) -> Callable[..., T]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        result = f(*args, **kwargs)
        print(f"{' '.join(str(arg) for arg in args)} {' '.join(f'{k}={v}' for k,v in kwargs.items())}")
        print(f"result: {result}\n")
        return result

    return wrapper


def is_palindrome(s: str) -> bool:
    """Return whether the given string s is a palindrome."""

    l = len(s)
    if l % 2 == 0:
        # Odd number of letters.
        mid = l // 2
        return all([s[i] == s[l - i - 1] for i in range(mid)])
    else:
        # Even number of letters.
        mid = l // 2 + 1
        return all([s[i] == s[mid - i] for i in range(mid)])


@log_each
def test_is_palindrome() -> tuple[int, ...]:
    """Test is_palindrome()."""

    results = []
    for length in range(1, 51):
        n_tests = 5 * pow(length, 4)
        count = 0
        for _ in range(n_tests):
            s = "".join(secrets.choice(string.ascii_lowercase) for _ in range(length))
            if is_palindrome(s):
                count += 1

        results.append((length, count / n_tests))

    return results


# ── Predicate ────────────────────────────────────────────────────────────────

def filter_even(numbers: list[int]) -> list[int]:
    return [number for number in numbers if number % 2 == 0]


def filter_odd(numbers: list[int]) -> list[int]:
    return [number for number in numbers if number % 2 != 0]


def increment(nums: list[int]) -> list[int]:
    return [num + 1 for num in nums]


def decrement(nums: list[int]) -> list[int]:
    return [num - 1 for num in nums]


def negate(nums: list[int]) -> list[int]:
    return [-num for num in nums]


def square(nums: list[int]) -> list[int]:
    return [num**2 for num in nums]


def cube(nums: list[int]) -> list[int]:
    return [num**3 for num in nums]


# ── Function ─────────────────────────────────────────────────────────────────

def show_table(rows: list[list[str]]) -> None:
    col_widths = [max(map(len, column)) for column in zip(*rows)]
    fmt = "{:" + " ".join(["<"+str(col_width)+""]*len(rows[0]))+"}\n"
