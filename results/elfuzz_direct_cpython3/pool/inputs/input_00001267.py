"""
This file contains a few examples of Python language features.
"""


import contextlib
from typing import (
	Annotated,
	Final,
	List,
	NamedTuple,
	Set,
	Tuple,
	TypeVar,
	Union,
	Iterator,
)

t = TypeVar("T")

T2 = TypeVar("T2", bound=int)


class A(object):
	pass
	
class B(A): # A is an ancestor of B
	pass
	
	
class C(B): # B is an ancestor of C
	pass

C() # OK
B() # OK
A() # NOT OK


# ── Context Manager ──────────────────────────────────────────────────────────


def context_manager_demo():
	with open("/dev/null") as f:
		f.read()
		
	with open("/dev/null", "rb") as f:
		f.read()


# ── Generators ───────────────────────────────────────────────────────────────


def generator_demo():
	generator_range_5 = range(5).__iter__()
	
	while True:
		next(generator_range_5)
		
		
generator_range_5 = range(5).__iter__()
next(generator_range_5) # => 0
next(generator_range_5) # => 1
next(generator_range_5) # => 2
next(generator_range_5) # => 3
next(generator_range_5) # => 4
try:
	next(generator_range_5) # => StopIteration exception!
except Exception as e:
	e # StopIteration


# ── Iterables and iterators ──────────────────────────────────────────────────


def iterable_iterator_demo():
	iterable_range_5 = range(5)
	
	list(iterable_range_5) # => [0, 1, 2, 3, 4]
	next(iterable_range_5) # => TypeError
	next(iterable_range_5.__iter__()) # => 0
	
	it = iter(range(5))
	try:
		while True:
			next(it)
	except StopIteration:
		pass
	else:
		raise RuntimeError()
	
		
iter(range(5)) # => <range_iterator object at 0x7f96bfc7d8a0>
list(iter(range(5))) # => [0, 1, 2, 3, 4]
next(iter(range(5))) # => StopIteration exception!


# ── Async Generators and Iterators ────────────────────────────────────────────


async def async_generator_demo():
	async for xdef json

def js_array_to_js_obj(
	js_object_json_str_list: List[JsonStr],
) -> List[JsObject]:
	return [
		json.loads(json_str)
		for json_str in js_object_json_str_list
	]


# ── ParamSpec ────────────────────────────────────────────────────────────────


def param_spec_demo() -> Tuple[Tuple[int, ...], int]:
	def wrapper(
		*p: int,
		x: int,
		y: int = 10,
		z: Final[int] = 100,
	) -> Tuple[int, ...]:
		pass

	return wrap(*range(10))


def test_param_spec() -> None:
	assert param_spec_demo() == ((10,), 10)


# ── Annotated ────────────────────────────────────────────────────────────────


def annotated_demo() -> None:

	class Person(NamedTuple):
		surname: str
		
	@contextlib.contextmanager
	def person_name(name: Annotated[str, "Surname"]) -> Iterator[str]:
		try:
			yield name
			
		finally:
			print(f"Goodbye {name}")
			
