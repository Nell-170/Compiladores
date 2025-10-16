# Caso 1: FOR con unpacking de tuplas
for a, b in [(1, 2), (3, 4)]:
    print(a, b)

# Caso 2: Asignación simple con unpacking
a, b = 10, 20
x, y, z = [1, 2, 3]

# Caso 3: Asignación con paréntesis
(m, n) = (5, 6)

# Caso 4: Unpacking con atributos
self.x, self.y = 1, 2

# Caso 5: FOR simple (sin unpacking, debe seguir funcionando)
for i in [1, 2, 3]:
    print(i)
