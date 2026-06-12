"""
Seed 01 — OOP, metaclasses, descriptors, decorators, context managers, generators
"""
import unittest
from typing import Any


class Field:
    def __init__(self) -> None:
        self._initialized = False

    def initialize(self):
        pass

    @property
    def initialized(self):
        return self._initialized


class CharField(Field):
    def __init__(self, max_length=None):
        super().__init__()
        self.max_length = max_length if max_length else 256
        self.value = ""

    def validate(self):
        if len(self.value) > self.max_length:
            raise ValueError(f"Max length is {self.max_length}")

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_value: str):
        self.validate()
        self.__value = new_value


class EmailField(CharField):
    def validate(self):
        super().validate()
        if "@" not in self.value:
            raise ValueError("Invalid email")


class PasswordField(CharField):
    def validate(self):
        super().validate()

        if len(self.value) < 8:
            raise ValueError("Password must be at least 8 characters long")

        has_uppercase = any([c.isupper() for c in self.value])
        has_lowercase = any([c.islower() for c in self.value])
        has_digit = any([c.isdigit() for c in self.value])

        if not (has_uppercase and has_lowercase and has_digit):
            raise ValueError(
                "Password must contain at least one uppercase letter, one lowercase letter, and one digit"
            )


class UserMeta(type):
    def __new__(cls, name: str, bases, attrs: dict[str, Any]):
        fields = {}
        for attr_name, attr_val in attrs.items():
            if isinstance(attr_val, Field):
                fields[attr_name] = attr_val

        if "__password__" not in fields or "__email__" not in fields:
            raise TypeError("User class must have '__password__' and '__email__' fields")

        return super().__new__(cls, name, bases, attrs)


class User(metaclass=UserMeta):
    __name__: CharField
    __age: int
    __email__: EmailField
    __password__: PasswordField
    __last_login: datetime.datetime
    __created_at: datetime.datetime
    __updated_at: datetime.datetime

    def __init__(
        self,
        name: str,
        age: int,
        email: str,
        password: str,
        last_login: datetime.datetime = datetime.datetime.now(),
        created_at: datetime.datetime = datetime.datetime.now(),
        updated_at: datetime.datetime = datetime.datetime.now(),
    ):
        self.__initialized = False
        self.__name = name
        self.__age = age
        self.__email = email
        self.__password = password
        self.__last_login = last_login
        self.__created_at = created_at
        self.__updated_at = updated_at
        self.initialize()

    def initialize(self):
        self.__initialized = True

    @property
    def initialized(self):
        return self.__initialized

    def save(self):
        print(f"{self} saved!")
        self.__update_at = datetime.datetime.now()

    def delete(self):
        print(f"{self} deleted!")

    def update_password(self, old_password: str, new_password: str):
        if old_password != self.password:
            raise ValueError("Old password is incorrect")
        self.password = new_password

    def change_email(self, old_email: str, new_email: str):
        if old_email != self.email:
            raise ValueError("Email is incorrect")
        self.email = new_email

    def __str__(self):
        return (
            f"<{type(self).__name__}: "
            f"name={self.name}, "
            f"age={self.age}, "
            f"email={self.email}>"
        )

    def __repr__(self):
        return (
            f"<{type(self).__module__}.{type(self).__qualname__}: "
            f"name={self.name}, "
            f"age={self.age}, "
            f"email={self.email}>"
        )


class CachedPropertyTests(unittest.TestCase):
    def test_cached_property(self):
        user = User("", "", "", "")

        with patch.object(user, "_User__initialized", True), \
             patch.object(User, "initialize"),\
             patch.object(user, "_User__name", "John Doe"):
            self.assertEqual(user.name, "John Doe")

        with patch.object(user, "_User__initialized", False), \
             patch.object(User, "initialize"),\
             patch.object(user, "_User__name", "Jane Doe"):
            self.assertNotEqual(user.namefrom .utils import (
    AnnotationType,
    ConcreteAnnotationType,
    _array_ctype,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


# ── Caching ───────────────────────────────────────────────────────────────────

T = TypeVar("T")
U = TypeVar("U")


def cached_property(fn: Callable[..., T]) -> property:
    """A property that caches its results."""
    attr_name = "_" + fn.__name__

    @property
    def wrapped(self) -> T:
        try:
            return getattr(self, attr_name)
        except AttributeError:
            value = fn(self)
            setattr(self, attr_name, value)
            return value

    return wrapped


@cached_property
def is_threaded() -> bool:
    return threading.active_count() > 1


@cached_property
def has_mmap_module() -> bool:
    """Check the availability of the `mmap` module.
    """
    try:
        import mmap   # noqa: F401
    except ImportError:
        return False
    return True


@cached_property
def is_windows() -> bool:
    """Determine if we're on a Windows machine.

    This function checks the OS name and version to determine if we're running
    under Windows. If you need more information about the current operating
    system, use the platform module instead.
    """
    return os.name == "nt"


@cached_property
def is_posix() -> bool:
    """Determine if we're on a POSIX-compliant Unix-like operating system.

    This function checks the OS name to determine if we're running under a
    POSIX-compatible Unix-like system. It does not guarantee that the system
    will be POSIX compliant (e.g., macOS). Use platform.system instead for a
    more comprehensive check.
    """
    return os.name == "posix" or sys.platform.startswith("linux") \
           or sys.platform.startswith("darwin") or sys.platform.startswith("cygwin")


@cached_property
def is_macos() -> bool:
    """Determine if we're on macOS."""

    if sys.platform.startswith('linux') and 'Darwin' in platform.mac_ver()[0]:
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
