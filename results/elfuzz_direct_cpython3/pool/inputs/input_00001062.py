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

array.array('h').frombuffer(bytes_object, 2)

array.array('I')[::-1].tolist()  # reverse order of an integer array
array.array('l')[::-1].tolist()  # reverse order of a long integer array
array.array('q')[::-1].tolist()  # reverse order of a quadlong integer array
array.array('L')[::-1].tolist()  # reverse order of an unsigned integer array
array.array('Q')[::-1].tolist()  # reverse order of an unsigned long integer array

array.array('s').tostring()  # returns the string representation

print(array.array('I').itemsize, array.array('l').itemsize, array.array('q').itemsize)

# ── Struct │ struct
import struct
struct.pack('>II', 0x1122334455667788, 0xaabbccddeeff00ff)
struct.unpack('>QQ', b'\1\0\0\0\0\0\0\0\2\3\4\5\6\7\8\9\10\11\12\13\14\15\16\17\20\21\22\23\0\1\2\3\4\5\6\7\8\9\0\1\2\3\4\5\6\7\8\9\0\1\2\3\4\5\6\7\8\9\0\1\2\3\4\5\6\7\8\9\0\1\2\3\4\5\6\7\8\9')


class TimeStruct:
    def __init__(self, *args):
        self.sec = args[0]
        self.nsec = args[1]


time_struct_instance = TimeStruct(time.time(), time.timezone)
print(struct.calcsize("<ii"))  # size of two integers on little-endian machine
buf = struct.pack("<IBBI", 0x00d5e4ed, 0x00010203, 0x04050607, 0x08090a0b)
print(struct.unpack(">HHBBII", buf))
print(buf[:8])
