import time

# Iniciar el cronómetro
inicio = time.time()

# lista básica
numeros = [1, 2, 3]

# append - agregar elemento al final
numeros.append(4)
numeros.append(5)

print(numeros)  # [1, 2, 3, 4, 5]

# sublist (slicing) - obtener sublista
sub = numeros[1:4]
print(sub)  # [2, 3, 4]

# remove por index usando del
del numeros[0]
print(numeros)  # [2, 3, 4, 5]

# remove por index usando pop
numeros.pop(2)
print(numeros)  # [2, 3, 5]

# Detener el cronómetro
fin = time.time()
duracion = (fin - inicio) * 1000  # convertir a milisegundos
print(f"\nTiempo de ejecucion: {duracion:.4f} milisegundos")

