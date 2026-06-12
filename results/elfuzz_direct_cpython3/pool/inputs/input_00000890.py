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
#
#     for object_ in objects:
#         print(object_)


if __name__ == '__main__':
    # Test the gc module.

    with GcCollect():

        a = [1] * 10 ** 6
        b = ('a', 'b') * 10 ** 5
        c = {'a': 1} * 10 ** 7
        d = {i: i**2 for i in range(10 ** 8)}
        e = (x for x in range(10 ** 9))
        f = []

        # Show the GC objects before garbage collection.
        print('Before:')
        for obj in gc.get_objects():
            print(obj)

        # Print the type of each object.
        for obj in gc.get_objects():
            print(type(obj))

        # Print the number of references to each object.
        for obj in gc.get_objects():
            print(id(obj), id(gc.get_referents(obj)))

        # Print the reference count of each object.
        for obj in gc.get_objects():
            print(sys.getrefcount(obj))

        # Print the cycle detection information for each object.
        for obj in gc.get_objects():
            try:
                print(gc.garbage.index(obj))
            except ValueError:
                pass

        # Print the cycle detection information for each object.
        for obj in gc.get_objects():
            try:
                print(gc.get_caches()[obj])
            except KeyError:
                pass