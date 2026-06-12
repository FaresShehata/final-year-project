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
import pickle
import sys
import types
import weakref
from abc import ABCMeta
from collections import deque
from copyreg import copy_reg
from types import CodeType


def _is_builtin_module(module_name):
    return hasattr(importlib.import_module(module_name), "__file__")


print(_is_builtin_module('os'))
print(_is_builtin_module('__main__'))

# ── Dis │ dis
dis.dis("a = True\nb = False\nc = [a, b]")
dis.dis("if (a and b): print(a)")
dis.dis("for i in range(10):\n\tcontinue")

# ── Ctypes │ ctypes
dll = ctypes.CDLL(None)
print(dll._handle)
print(type(dll._handle))
libm = ctypes.CDLL('libc.so.6')  # load system library “libc”
print(libm._handle)
print(dir(ctypes))

data = (
    ("a", "A"),
    ("b", "B"),
    ("c", "C")
)
arr = array.array("u", data[0])
arr.append(data[1][0])
arr.reverse()
arr.insert(0, data[1][1])

ctypes.memmove(arr.buffer_info()[0] + 1, arr.buffer_info()[0], len(data[1]))
arr[0], arr[-1] = arr[-1], arr[0]

memview = memoryview(array.array('i', list(range(10))))
memview[::3] += memview[1::3]
del memview

# ── Array │ array
array.array('B')
array.array('B', (ord(c) for c in "abcde"))
array.array('I')  # signed integers are not supported
array.array('f')

byte_string = b"abcde"
bytes_array = bytes(byte_string)
bytes_object = str(byte_string).encode()

array.array('H').fromstring(byte_string)
array.array('H').tobytes() == byte_string
array.array('h').tostring() != byte_string
array.array('Q').tostring() != byte_string
array.array('q').tostring() != byte_string

struct.Struct('HH').pack_into("", 0, 1, 2)
struct.Struct('HH').unpack_from(bytes(byte_string))[:2]

buffer_info = buffer(byte_string).__getattribute__('buf')
array.array('H').frombuffer(buffer_info, 0, 2)
pickle.dumps(tuple(range(10)))
pickle.loads(b'\x80\x04\x95\xc2\x03\x00\x00\x00\x00\x00\x00\x00]\x93.'
             b'\x0c(\x8c\x03spam\x94)\x8c\x01egg\x94S.')
pickle.dumps((None, (), [], {}, set(), b"", bytearray()))
pickle.dumps([range(10)])
pickle.dumps(lambda x: x ** 2)  # TypeError: a 'lambda' is not JSON serializable
pickle.dumps(sys.modules[__name__].__loader__)  # AttributeError: module 'sys' has no attribute '__loader__'
pickle.dumps(sys.path)

# ── CopyReg │ copy_reg
copy_reg.pickle(dict, dict.copy)  # register custom pickling function for dictionaries
copy_reg.dispatch_table[id(dict)] = dict.copy  # override default