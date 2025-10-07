# FAIL: grammar allows only one comp_op between two arithmetic_expr.
# Chained comparisons like a < b < c aren’t supported.
a = 1
b = 2
c = 3
flag = a < b < c
