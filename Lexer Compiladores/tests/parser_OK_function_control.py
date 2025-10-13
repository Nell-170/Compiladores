# Control flow INSIDE a function (allowed by your func_body_stmts)
def f(a, b):
    c = a + b
    if c > 10:
        return c
    elif c == 10:
        return 0
    else:
        i = 0
        while i < 3:
            if i == 1:
                i += 1
                continue
            i += 1
        total = 0
        for k in lst:
            total += k
        return total
