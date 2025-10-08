# Top-level simple statements + expression precedence
x = 1
y = 2
z = -2**3 + +y * (x + 4) // 2 % 3
w = (x,)            # one-element tuple
t = (x, y, z)       # multi-element tuple
lst = [x, y, z]     # list
dct = {"a": x, "b": y + 1, True: 5}

# Calls with positional args only
print("ok", x, y, z)
