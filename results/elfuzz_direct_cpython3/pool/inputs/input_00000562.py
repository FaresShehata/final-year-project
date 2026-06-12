"""


Given a list of ingredients `i` and a flavour `f` as input, create a function
that returns the list, but with the elements `bread` around the selected
ingredient.

### Examples

    make_sandwich(["tuna", "ham", "tomato"], "ham") ➞ ["tuna", "bread", "ham", "bread", "tomato"]
    
    make_sandwich(["cheese", "lettuce"], "cheese") ➞ ["bread", "cheese", "bread", "lettuce"]
    
    make_sandwich(["ham", "ham"], "ham") ➞ ["bread", "ham", "bread", "bread", "ham", "bread"]

### Notes

  * You will always get valid inputs.
  * Make two separate sandwiches if two of the same elements are next to each other (see example #3).

"""

def make_sandwich(i, f):
    res = []
    while i:
        if not f in res or res[-1] != f: res.append('bread')
        if i[0] == f: res.append(f)
        else: res.append(i.pop(0))
        if len(res) > 4 and res[-2:] == ['bread', f]: res.pop(-2), res.pop(-2)
​
    return res