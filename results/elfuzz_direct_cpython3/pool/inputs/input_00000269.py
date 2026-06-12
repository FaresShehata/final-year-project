"""
Seed 04 — Low-level Python: bytecode introspection, dis, code objects, ctypes,
          struct, array, memoryview, pickle, copyreg, marshal, importlib,
          contextlib, functools, itertools, operator, collections, typing,
          enum, warnings, logging, traceback.
"""

# You should have a good grasp of Python language so far. This is a very low-level module that will help you understand how Python works under-the-hood.

import types

def f():
    x = 1<<23
    y = x+1
    return y/x


print(f())

codeobj = types.CodeType(
        0, #co_argcount
        0, #co_kwonlyargcount
        0, #co_nlocals
        0, #co_stacksize
        0, #co_flags
        b'f', #co_code
        (None,), # co_consts
        ('x','y'), # co_names
        (), # co_varnames
        None, # co_filename
        '<stdin>', # co_name
        1,#co_firstlineno
        None, # co_lnotab
        ())



dis.disassemble(codeobj)

from dis import dis as disassemble_py
disassemble_py(codeobj)