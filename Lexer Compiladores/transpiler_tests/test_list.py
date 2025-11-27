# Test básico de listas
a = [1, 2, 3]
print(a)

# Acceso a elementos
print(a[0])
print(a[1])

# Longitud
print(len(a))

# Iteración
for i in a:
    print(i)

# Lista con strings
b = ["hola", "mundo"]
print(b)

# Lista vacía es falsy
empty = []
if not empty:
    print("Lista vacía es falsa")
