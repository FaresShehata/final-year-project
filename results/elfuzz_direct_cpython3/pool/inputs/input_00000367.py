"""
Seed 04 — Low-level Python: bytecode introspection, dis, code objects, ctypes,
          struct, array, memoryview, pickle, copyreg, marshal, importlib, sys
"""

import gc

from functools import wraps


def gc_collect(times=3):
    """ Call GC collect `times` times. """
    for _ in range(times):
        gc.collect()
        yield gc.get_objects()


class GcCollect:
    def __init__(self) -> None:
        self._objects = set()

    def __enter__(self):
        """ Called when entering the with statement. """
        # Get all current objects.
        self._objects.update(gc.get_objects())
        return self

    def __exit__(self, *args):
        """ Called when exiting the with statement. """
        # Collect garbage and remove collected objects from the set of current objects.
        self._objects -= set(gc_collect())


# def show_gc_objects(objects=None):
#     if not objects:
#         objects = gc.get_objects()
#     print('\n'.join(f'{obj.__class__} {id(obj)}' for obj in objects))


def gc_collect(times=3):
    """ Call GC collect `times` times. """

    @wraps(gc_collect)
    def wrapper(*args, **kwargs):
        for _ in range(times):
            gc.collect()

    return wrapper