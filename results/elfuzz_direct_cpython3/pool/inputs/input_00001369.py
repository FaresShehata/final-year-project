"""
Seed 03 — Functional programming: closures, higher-order functions, comprehensions,
          generators, coroutines (send/throw/close), itertools, functools,
          decorators, context managers
"""


def gcd(a: int, b: int) -> int:
    """Euclidean algorithm for greatest common divisor."""
    while a != 0 and b != 0:
        if a > b:
            a %= b
        else:  # a < b
            b %= a
    return max([a, b])


# Return the smallest of two arguments.
min2 = lambda x, y: x if x <= y else y

# A decorator is a function that takes another function as an argument, add some functionality and returns it back.
@functools.cache
def fibonacci(n: int):
    """Return the n-th Fibonacci number."""
    if n == 1 or n == 2:
        result = 1
    elif n % 2 == 0:
        result = fibonacci(n // 2) ** 2
    else:
        result = fibonacci((n - 1) // 2 + 1) * fibonacci((n - 1) // 2)
    return result


# A recursive example with memoization.
@functools.lru_cache(maxsize=None)
def fib(n: int):
    """
    Calculate the n-th Fibonacci number using recursion.

    :param n: The index of the Fibonacci number to be calculated.
    :return: The n-th Fibonacci number.
    """
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n-1) + fib(n-2)


# A simple integer counter that increments each time the function is called.
count = 0


def increment_count():
    global count
    count += 1
    return count


increment_count()


# Check whether the given number is a prime number.
def is_prime(x: int):
    """
    Determine whether the given number is a prime number.

    :param x: The number to check.
    :return: True if the number is prime, False otherwise.
    """
    if x < 2:
        return False
    if x == 2:
        return True
    if x % 2 == 0:
        return False
    i = 3
    while i * i <= x:
        if x % i == 0:
            return False
        i += 2
    return True


# Get all prime numbers up to a given limit.
def primes(limit=10_000):
    """
    Generate prime numbers up to a given limit.

    :param limit: The upper limit for generating prime numbers.
    :yield: Prime numbers less than or equal to the limit.
    """
    yield 2
    for num in range(3, limit+1, 2):
        if is_prime(num):
            yield num


# Create a list comprehension for squares of even numbers between 1 and 10.
squares_of_evens = [x**2 for x in range(1, 11) if x%2==0]

# Create a dictionary using dictionary comprehension with keys being strings and values being their lengths.
word_lengths = {word:len(word) for word in ['hello', 'world']}

# Create a set comprehension containing only odd numbers from 1 to 99 inclusive.
odd_numbers = {num for num in range(1, 100, 2)}

# Create a generator expression for cubes of odd numbers between 1 and 10.
cubes_of_odds = (x**3 for x in range(1, 11) if x%2)

# Flatten a nested tuple into a flat structure using a generator expression.
flat_tuple = (*(*nested_tuple,),)

# Create a generator expression using conditional expressions with multiple conditions.
filtered_values = (value for value in iterable if condition_one(value) and condition_two(value))

# Iterate over the items in a dictionary using a dictionary view object.
for key, value in dict.items():

# Convert a list of integers to a single string by joining them with commas using a join operation.
string_list = ','.join(str(item) for item in my_list)


# Define a custom class named Person.
class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age
    
    # An instance method that prints out the person's name and age.
    def display_info(self):
        print(f'Person\'s Name: {self.name}, Age: {self.age}')


person = Person("John Doe", 30)
person.display_info()

# Build a class hierarchy with inheritance where Student inherits from Person.
class Student(Person): 
    def __init__(self, name: str, age: int, grade: str):
        super().__init__(name, age)  # Call the constructor of the parent class
        self.grade = grade
    
    # Method specific to students
    def get_grade(self):
        return f'{self.grade}'

student = Student("Jane Smith", 18, "A")
print(student.get_grade())


# Implement a class hierarchy with multiple inheritance where Teacher also inherits from Student.
class Teacher(Student):
    def __init__(self, name:str, age:int, subject:str):
        super().__init__(name, age)
        self.subject = subject
    
    def teach(self):
        print(f'Teaching subject {self.subject}')

teacher = Teacher("Bob Brown", 40, "Mathematics")
teacher.teach()
student.display_infoclass Priority(enum.IntEnum):
    LOW    = 1
    NORMAL = 5
    HIGH   = 10
    URGENT = 20


class Flag(enum.Flag):
    A = 1 << 0  # bitfield flag type
    B = 1 << 1  # bitfield flag type
    C = 1 << 2  # bitfield flag type

    D = A | C  # compound assignment of flags
    E = (C | B) - C  # subtraction and bitwise complement

    @classmethod
    def from_hex(cls: type[Flag], hexstr: str) -> Flag:
        """Create flags from hexadecimal string."""
        bits = int(hexstr.lstrip('0x'), base=16)
        return cls(bits)


@runtime_checkable
class IterableWithIndex(Protocol[K, V]):  
    def __iter__(self) -> Iterator[V]:
        ...

    def __getitem__(self, index: K) -> V:
        ...  


