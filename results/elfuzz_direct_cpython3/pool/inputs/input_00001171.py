"""
Type hints as described here are a subset of the full Python 3.8 specification.
See https://docs.python.org/3/library/typing.html#module-contents ."""

from typing import *
import sys
from collections.abc import Iterable
from functools import partial
from inspect import signature
from itertools import chain, repeat
from operator import itemgetter
from random import randint
import re
import time
from types import UnionType
from warnings import warn as warning

try:
    from mypy_extensions import _CallableT as Callable
except ImportError:
    # Backport for <Python 2.7
    def Callable(*args): return type('', (), {})() if len(args) == 0 else args[0]
from pyglet.window.key import KeyNames, KEY_BACKSPACE, KEY_DELETE, KEY_SPACE
from pyglet.window.key import MOD_CTRL, MOD_SHIFT, MOD_ALT, MOD_NUMPAD, MOD_CAPSLOCK, MOD_RESERVED1, MOD_RESERVED2
from pyglet.window import key
from . import event
from . import util


__all__ = ['Event', 'EventType', 'EventValue',
           'KeyMap', 'KeyEvent', 'MouseEvent', 'WheelEvent', 'WindowResizeEvent', 'TimerEvent']


class Event(event.Event):
    """A generic event that holds additional information about an event."""

    __slots__ = ('_target', '_user_data')

    def __init__(self, target=None, user_data=None):
        super().__init__()
        self._target = target
        self._user_data = user_data

    @property
    def target(self):
        return self._target

    @property
    def user_data(self):
        return self._user_data

    def set_target(self, target):
        self._target = target

    def set_user_data(self, data):
        self._user_data = data


# -------------------------------------------------------------------- #
#                             EventTypes                               #
# -------------------------------------------------------------------- #

def format_event_type(type_name):
    return '%s.%s' % (type.__module__, type_name)

class EventType(Tuple[int]):
    """An enumeration representing an event."""

    __slots__ = ()

    def __new__(cls, *values):
        if not values:
            raise TypeError('expected at least one argument')
        return Tuple.__new__(cls, values)

    def __contains__(self, value):
        return value in self._as_tuple()

    def convert_value_to_enum(self, value, default=NoDefault):
        v = None
        try:
            v = int(value)
        except ValueError:
            pass
        else:
            if v >= 0 and v <= max(self):
                return v
        if default is NoDefault:
            raise KeyError('%r is not a member of %s. Valid members are:\n\t%s' %
                           (value, self.__name__,
                            '\n\t'.join(map(str, self))))
        return default

    def get_member(self, value):
        v = self.convert_value_to_enum(value)
        return object.__getattribute__(self, '__members__.get(%d)' % v)

    def get_members(self):
        "Return a dictionary mapping integer identifiers to member objects."
        m = {}
        for name in dir(self):
            obj = getattr(self, name)
            if isinstance(obj, Member):
                m[obj.id] = obj
        return m

    @classmethod
    def from_member_id(cls, id):
        return object.__getattribute__(cls, '__members__[%d]' % id)

    @classmethod
    def from_member_name(cls, name):
        return object.__getattribute__(cls, '__members__[%s]' % repr(name))

    @classmethod
    def keys(cls):
        """
<|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|>        Returns a list of strings containing all valid event names.

        :rtype: list[str]
        """
        return [e.value for e in cls]

    @classmethod
    def values(cls):
        """
        Returns a list of lists where the first element contains