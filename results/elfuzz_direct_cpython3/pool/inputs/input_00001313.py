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
        else:
            b %= a
    return max((a + b))


gcd(48, 18)


A = [1, 2, 3]
B = [x + 1 for x in A]

C = []
for x in A:
    C.append(x + 1)

D = set(A)
E = frozenset(B)
F = {x ** 2 for x in D}

G = dict()
for i in range(len(D)):
    G[i] = D.pop()

H = sum([i ** 2 for i in D])

I = lambda n: str(n).zfill(3)
J = I(98765)

K = lambda n=6, m="hello": f"{n} {m}"
L = K("world")

M = {"name": "John", "age": 30}


class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age


N = Person(name="Alice", age=25)


O = lambda x, y, z=5: x + y + z


P = O(1, 2, 3)


Q = lambda *args: args  # Tuple unpacking.


R = lambda **kwargs: kwargs.get('key', 'default')  # Dict unpacking.

S = lambda x: [y for y in x]  # List comprehension
T = S(range(10))
U = sorted(T, reverse=True)


V = lambda x, *, y=None, z=None: x + y + z


W = V(5, 2, z=3)  # Only one argument is required here, so it's possible to omit the second parameter.

X = V(z=3)(1, 2)  # Even though we don't provide any arguments, the function can be called with positional parameters.

Y = lambda x, y: x % y == 0
Z = Y(10, 2)  # True


AA = lambda x, y=lambda x: x: x + y(x)  # Recursive call


BB = AA(lambda x: x**2)
CC = BB(5)

DD = lambda x=lambda x: x*2: x(lambda x: x+1)(5)


EE = BB(CC)

FF = lambda x: lambda y: x + y
GG = FF(2)(3)

HH = lambda x: lambda y: lambda z: x + y + z
II = HH(1)(2)(3)


JJ = lambda x: lambda y: lambda z: x + y + z
KK = JJ(1)(2)(3)

LLL = lambda x: lambda y: lambda z: x + y + z
MMM = LLL(1)(2)(3)

NNN = lambda x: lambda y: lambda z: x + y + z
PPP = NNN(1)(2)(3)

QQQ = lambda x: lambda y: lambda z: x + y + z
RRR = QQQ(1)(2)(3)

ZZZ = lambda x: lambda y: lambda z: x + y + z
AAAA = ZZZ(1)(2)(3)

BBBB = lambda x: lambda y: lambda z: x + y + z
CCCC = BBBB(1)(2)(3)

DDDD = lambda x
# Multiply every element in the list `numbers` by 2.
[lambda x: x * 2(number) for number in numbers]


# Use the generator from the previous seed to calculate prime numbers.
prime_generator = primes()