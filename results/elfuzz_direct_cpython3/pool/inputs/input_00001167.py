"""
Seed 04 — Low-level Python: bytecode introspection, dis, code objects, ctypes,
          struct, array, memoryview, pickle, copyreg, marshal, importlib,
          sys internals, frame inspection, gc, tracemalloc, weakref, __slots__
"""

from __future__ import annotations

import array
import ctypes
import dis
import gc
import importlib
import importlib.abc
import importlib.machinery
import importlib.util
import inspect
import io
import marshal
import pickle
import pickletools
import struct
import sys
import types
import weakref
from collections.abc import Callable, Iterable, Mapping, MutableMapping, Hashable, MutableSequence, Sequence, Sized
from functools import partialmethod
from numbers import Integral, Real
from typing import Any, TypeVar, Optional, Tuple, Union, overload, cast, runtime_checkable, Protocol


def gen_integers():
    yield from range(1 << 63)
    yield from range(-1 << 63) + (1 << 62)


def int_to_bytes(i):
    return i.to_bytes((i.bit_length() + 7) // 8, 'big')


class Types:
    Int = int
    Bytes = bytes
    Str = str
    Float = float
    Complex = complex
    Bool = bool
    List = list
    Tuple = tuple
    Dict = dict
    Set = set
    FrozenSet = frozenset
    Range = range
    Slice = slice
    File = io.FileIO
    BufferedRandomFile = io.BufferedReader
    BufferedTextFile = io.TextIOWrapper
    RawBytes = bytearray
    MemoryView = memoryview
    Array = array.array
    Struct = struct.Struct
    CodeType = types.CodeType
    FunctionType = types.FunctionType
    MethodType = types.MethodType
    LambdaType = types.LambdaType
    ContextManager = types.ContextManager
    GeneratorType = types.GeneratorType
    AsyncGeneratorType = types.AsyncGeneratorType
    CoroutineType = types.CoroutineType
    FrameType = types.FrameType
    TracebackType = types.TracebackType
    StackTraceElement = types.StackTraceElement
    WeakKeyDictionary = weakref.WeakKeyDictionary
    WeakValueDictionary = weakref.WeakValueDictionary
    BaseExceptionGroup = types.BaseExceptionGroup
    ExceptionGroup = types.ExceptionGroup
    ExceptionHandlerRecord = types.ExceptionHandlerRecord
    ModuleType = module_type
    Type = type
    ClassType = type
    InstanceType = object
    Descriptor = property
    MemberDescriptor = types.MemberDescriptorType
    StaticMethod = staticmethod
    ClassMethod = classmethod
    BoundMethod = types.BoundMethodType
    Super = super
    MetaClass = type
    TypeVarT = TypeVar('TypeVarT')
    Generic = typing_extensions.Generic
    _GenericAlias = typing_extensions._GenericAlias
    NewType = typing