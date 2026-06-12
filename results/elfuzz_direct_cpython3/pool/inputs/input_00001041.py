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

    def __init__(self, **kwargs) -> None:
        for field, val in kwargs.items():
            setattr(self, f"_{field}", val)

   