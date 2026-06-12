"""
Seed 04 — Low-level Python: bytecode introspection, dis, code objects, ctypes,
          struct, array, memoryview, pickle, copyreg, marshal, importlib,
          typing, typing_extensions, dataclasses, contextlib, functools, itertools,
          abc, inspect, abc, weakref, trace, signal, logging, time, pprint, reprlib,
          enum, math, fractions, decimal, unittest, os, sys, random, hashlib,
          base64, zlib, binascii, urllib.request, http.client, cgi, email.utils,
          re, traceback, threading, queue, multiprocessing, subprocess, shlex,
          socket, selectors, select, ssl, sqlite3, yaml, json, xml.etree.ElementTree,
          doctest, unittest.case, unittest.loader, unittest.runner, unittest.result,
          unittest.suite, unittest.testcase, unittest.util, unittest.main, unittest.mock,
          collections.abc, collections.defaultdict, collections.deque, collections.namedtuple,
          collections.OrderedDict, collections.Counter, collections.ChainMap,
          collections.UserDict, collections.UserList, collections.UserString,
          collections.MappingProxyType, collections.deque.extendleft, collections.deque.appendleft,
          collections.deque.popright, collections.deque.popleft, collections.deque.rotate,
          collections.deque.reverse, collections.deque.sort, collections.deque.count,
          collections.deque.index, collections.deque.insert, collections.deque.remove,
          collections.deque.clear, collections.deque.copy, collections.deque.__eq__,
          collections.deque.__ne__, collections.deque.__contains__, collections.deque.__len__,
          collections.deque.__getitem__, collections.deque.__setitem__, collections.deque.__delitem__,
          collections.deque.__iter__, collections.deque.__reversed__, collections.deque.__add__,
          collections.deque.__mul__, collections.deque.__rmul__, collections.deque.__imul__,
          collections.deque.__iadd__, collections.deque.__isub__, collections.deque.__idiv__,
          collections.deque.__itruediv__, collections.deque.__ifloordiv__, collections.deque.__ilshift__,
          collections.deque.__irshift__, collections.deque.__ior__, collections.deque.__ixor__,
          collections.deque.__neg__, collections.deque.__pos__, collections.deque.__abs__,
          collections.deque.__invert__, collections.deque.__complex__, collections.deque.__int__,
          collections.deque.__float__, collections.deque.__round__, collections.deque.__trunc__,
          collections.deque.__floor__, collections.deque.__ceil__, collections.deque.__str__,
          collections.deque.__repr__, collections.deque.__format__, collections.deque.__lt__,
          collections
# ── Code object utilities ─────────────────────────────────────────────────────

def get_code_object(fn) -> types.CodeType:
    return fn.__code__

def dump_code_object(code) -> str:
    # NB: `dis` function doesn’t work with only the code object (it needs to be an
    #     instance of a code type).
    code_obj = types.CodeType(
        code.co_argcount,
        code.co_kwonlyargcount,
        code.co_nlocals,
        code.co_stacksize,
        code.co_flags,
        code.co_code,
        code.co_consts,
        code.co_names,
        code.co_varnames,
        code.co_filename,
        code.co_name,
        code.co_firstlineno,
        code.co_lnotab,
        code.co_freevars,
        code.co_cellvars,
    )
    return annotated_disassembly(code_obj)


# ── Low-level types and operations ────────────────────────────────────────────

def test_ctypes():
    return ctypes.c_int32(789456123) == ctypes.c_ulonglong(789456123)

def test_struct():
    x = array.array('i', [789456123])
    print(x.itemsize)
    
    return struct.unpack('>I', b'\x7\x8\x9\x4\x5\x6\x1\x2')[0]

def test_pickle():
    x = array.array('i', [789456123])

    data = pickle.dumps(x)
    print(pretty_marshal(data))

    y = pickle.loads(data)
    assert x.tolist() == y.tolist()

    z = bytearray([1, 2, 3])
    data = pickle.dumps(z)
    w = pickle.loads(data)
    assert list(w) == [1, 2, 3]


# ── Memoryview utilities ──────────────────────────────────────────────────────

def test_memoryview():
    x = array.array('u')
    x.frombytes(b"Hello world!\0")
    mv = memoryview(x)
    mv[1::2].readonly = True
    assert mv.readonly is True


# ── Pickle tools utility functions ────────────────────────────────────────────

def show_opcode_table(opcodes=None):
    """
    Display opcode table.
    """
   