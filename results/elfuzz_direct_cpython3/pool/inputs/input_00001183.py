"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""
from typing import Any

import asyncio
from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    x: int = 1
    y: float | None = None
    z: bool = False
    a_float: float = 3.456

    @property
    def coords(self) -> tuple[int, float]:
        return self.x, self.y or self.a_float


# ── Async Await ───────────────────────────────────────────────────────────────-

async def fetch_url(url: str) -> str:
    await asyncio.sleep(0.1)
    return url


async def main():
    print("\nASYNC AWAIT 👩‍💻")
    url = "http://www.google.com"
    result = await fetch_url(url)
    print(result)


# ── Protocols ─────────────────────────────────────────────────────────────────

async def process_data(data: bytes) -> str:
    return data.decode("utf-8")


async def main_protocol():
    print("\nPROTOCOLS 🌐")
    raw_bytes = b"\x00\x01\x02\x03ABCDEF\xFF"
    processed = await process_data(raw_bytes)
    print(processed)


# ── Dataclasses ────────────────────────────────────────────────────────────────

def create_point() -> Point:
    point = Point()
    
    point.x = 99
    
    for k, v in point.__dict__.items():
        print(k, v)
    
    
create_point()


# ── Slots ──────────────────────────────────────────────────────────────────────

print('\nSLOTS 🎟️')


class Person:
    
    __slots__ = ('_name', '_age')
    
    def __init__(self, name: str, age: int):
        self._name = name
        self._age = age
        
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def age(self) -> int:
        return self._age
    
    def __repr__(self) -> str:
        return f'Person(name={self.name}, age={self.age})'
    

person = Person('John Doe', 30)
print(person)

try:
    person._invalid_property = 'something'
except AttributeError:
    print('AttributeError')

with person as p:
    print(p)


# ── Structural Pattern Matching ────────────────────────────────────────────────

def describe_pet(animal: str, pet: dict[str, str] | None = None) -> None:
    if animal == 'dog':
        name = pet['name']
        age = pet['age']
        breed = pet.get('breed')
        owner_name = pet.get('owner') or 'no one'
        
        if not breed:
            print(f"{name} is {age} years old.")
            
        else:
            print(f"{name} is a {breed} breed. They are {age} years old.")
            
        print(f"They belong to {owner_name}.")
        
    elif animal == 'cat':
        name = pet['name']
        age = pet['age']
        color = pet.get('color') or 'unknown'
        owner_name = pet.get('owner') or 'no one'
        vaccinated = pet.get('vaccinated', True)
        
        print(f"{name} is a {color} cat who is {age} years old.")
        
        if vaccinated:
            print(f"He was vaccinated.")
            
        else:
            print(f"He was not vaccinated.")
            
        print(f"They belong to {owner_name}.")
        
    else:
        print(f"Don't know        hint = get_type_hints(cls)[Annotated]
        
        # Validate type of underlying value.
        try:
            match hint.base:
                case Annotated(base=base_hint):
                    return self._read_value(obj, base_hint)
                    
                case TypeVar():
                    return hint.copy_validators(hint)(obj)
                
                case _:
                    assert isinstance(hint, type)
                    assert isinstance(obj, hint)
                    
        except Exception as e:
            raise ValueError(
                f"Invalid type {type(obj).__name__}: {e}",
            ) from e
        
        # Run validator against underlying value.
        try:
            return hint.validate(obj)
        except Exception as e:
            raise ValueError(
                f"Invalid value {repr(obj)}: {e}",
            ) from e
    
    
    def _write_value(self, obj: object | None, cls: type[T]) -> None:
        """Validate and store annotated type in the underlying value."""
        
        assert isinstance(obj or cls, Annotated), \
            f"{cls.__name__} must be annotated with Annotated."
        
        # Extract annotation from the class.
        hint = get_type_hints(cls)[Annotated]
        
        # If the underlying object is already annotated, use its validators.
        if isinstance(obj, Annotated):
            hint = obj.annotated
        
        # Validate value's type.
        hint.validate(obj)


@typing.overload # type: ignore[misc]
def Annotated[T](hint: type[T], *args: Any, **kwargs: Any) -> Annotated[T]:
    ...


@typing.overload # type: ignore[misc]
