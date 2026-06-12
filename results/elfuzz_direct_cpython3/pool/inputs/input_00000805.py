"""
Seed 04 — Low-level Python: bytecode introspection, dis, code objects, ctypes,
          struct, array, memoryview, pickle, copyreg, marshal, importlib, timeit
"""
from __future__ import print_function

import marshal
import struct
import sys
from datetime import datetime
from inspect import ismodule
from io import BytesIO
from types import CodeType
from typing import Any, Dict, List, Optional, Tuple


def main() -> None:
    """
    Seed 04 - low level python
    """

    # ------------------------------------------- #
    # Disassembling and compiling source code     #
    # ------------------------------------------- #

    # The following examples show how to use the dis module that provides a very simple way
    # of viewing the bytecode for a given function. It does not try to provide much more than this.
    # Also note that it can be imported from the built in dis module, or from the dis module in
    # the dis standard library package.

    # Let's start with an example of a simple hello world program which prints 'Hello World'.

    def hello_world():
        """Print "Hello World"."""
        print("Hello World")

    dis.dis(hello_world)

    # We get the following output:

    #   1           0 LOAD_NAME                0 (print)
    #               2 LOAD_CONST               0 ('Hello World')
    #               4 CALL_FUNCTION            1
    #               6 POP_TOP
    #               8 LOAD_CONST               1 (None)
    #              10 RETURN_VALUE

    # This shows several things:

    #   1) There are two instructions; they take up 3 bytes each when encoded in the bytecode.
    #      The first one loads the name 'print' into the local variable set by the compiler.
    #      The second one loads the string literal 'Hello World' into another local variable.
    #      Then there is a call to the name "print" passing the argument loaded in the previous step.
    #      Finally we pop the top item off the stack because we do not need it anymore.
    #   2) When loading names and literals, we see the opcode number, then followed by the index in
    #      the name list (or constant pool). Note that the index starts at zero!
    #   3) The next few opcodes like POP_TOP, and LOAD_CONST all have fixed length byte codes.
    #      However, CALL_FUNCTION has a variable length depending on the number of arguments passed.
    #      Here we pass only one argument so the length