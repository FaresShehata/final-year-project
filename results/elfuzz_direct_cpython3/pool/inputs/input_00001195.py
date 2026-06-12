"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching, and more 🎉
"""

import datetime
import time
from typing import Awaitable, Callable, Dict, NamedTuple, Optional, Sequence, Tuple, TypeVar, Union

# If you see "not enough arguments for call to", it's because the function expects keyword-only parameters.
def func(x: int = 1) -> None:
    pass


func(42)

# --> TypeError: func() missing 1 required positional argument: 'y'

class Person:
    name: str
    age: int
    
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age
        
p = Person("Jim", 37)
print(p.name, p.age)

# # Instance attributes are not part of the class definition: they're created at runtime!
# print(Person.__dict__)
# # {'__module__': '__main__', 
# #  '__doc__': 'Instance attributes are not part of the class definition: they\\\'re created at runtime!', 
# #  'name': <attribute 'name' of \'Person\' objects>, 
# #  'age': <attribute 'age' of \'Person\' objects>, 
# #  '__init__': <function __init__ at 0x7f6958c8b0d0>}
    
# print(dir(Person))
# # ['__annotations__', 
# #  '__call__', 
# #  '__class__', 
# #  '__delattr__', 
# #  '__dict__', 
# #  '__dir__', 
# #  '__doc__', 
# #  '__eq__', 
# #  '__format__', 
# #  '__ge__', 
# #  '__getattribute__', 
# #  '__gt__', 
# #  '__hash__', 
# #  '__init__', 
# #  '__init_subclass__', 
# #  '__le__', 
# #  '__lt__', 
# #  '__module__', 
# #  '__ne__', 
# #  '__new__', 
# #  '__reduce__', 
# #  '__reduce_ex__', 
# #  '__repr__', 
# #  '__setattr__', 
# #  '__sizeof__', 
# #  '__str__', 
# #  '__subclasshook__', 
# #  '__weakref__', 
# #  'age', 
# #  'name']
  
# print(type(getattr(Person, "__annotations__")))
# # <class 'dict'>  
   
# # We can initialize a new instance using the constructor method defined in the class.
#