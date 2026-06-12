"""
Seed 01 — OOP, metaclasses, descriptors, decorators, context managers, generators
"""

# TODO: Check why I can't import from other files (using relative imports)
from .helpers import *
import random


# TODO: Create a class that has an attribute which is a list of another class instances and another attribute which is a method to add new elements to the list.
class MyClass:
    def __init__(self):
        self.my_list = []
        self.add_element(self)

    @staticmethod
    def add_element(obj):
        obj.my_list.append(obj)


obj_1 = MyClass()
print("Object 1:", obj_1)
obj_2 = MyClass()
print("Object 2:", obj_2)
obj_3 = MyClass()
print("Object 3:", obj_3)
print("My List:", [o for o in obj_1.my_list])


# TODO: Create a class that has an attribute which is a dictionary with keys being strings and values being integers.
# Then create two methods:
# - one that sets a key-value pair if the key does not exist yet and another that updates the value corresponding to a given key by adding the argument passed as parameter.

class MyDictionary:
    def __init__(self):
        self.dict = {}

    def set_value_if_missing(self, key, value):
        if key not in self.dict.keys():
            self.dict[key] = value

    def update_value(self, key, value_to_add):
        if key in self.dict.keys():
            self.dict[key] += value_to_add
        else:
            print(f"Key '{key}' doesn't exist in the dictionary.")


my_dict = MyDictionary()
for i in range(5):
    my_dict.set_value_if_missing(random.randint(0, 9), random.randint(0, 9))
print(my_dict.dict)

my_dict.update_value(7, 4)
my_dict.update_value(6, 8)
print(my_dict.dict)