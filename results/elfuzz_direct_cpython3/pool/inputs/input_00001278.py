"""Napisz program, który na podstawie listy liczb całkowitych
wyświetli sumę, iloczyn oraz średnią arytmetyczną.

Przykład: [10, 2, 3, -5] -> suma = 8 | iloczyn = 60 | srednia = 2.67"""

lista=[10,2,3,-5]
suma=0
iloczyn=1
for liczba in lista:
    print(liczba)
    suma +=liczba
    iloczyn *=liczba
print("srednia")
print(suma/len(lista))
print(suma)