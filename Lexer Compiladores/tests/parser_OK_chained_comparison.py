# Chained comparisons like a < b < c should be supported
a = 1
b = 2
c = 3
flag = a < b < c

ok1 = a < b < c
ok2 = a < b <= c != d
ok3 = (a + 1) < (b * 2) < (c ** 3)
ok4 = not (a < b < c) and a == b

a + 1 < b*2 < c**3