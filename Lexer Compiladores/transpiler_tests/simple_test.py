import time

# Iniciar el cronómetro
inicio = time.time()

a = 5
b = 10
c = a + b

if a < b:
    d = a * 2
else:
    d = b * 2

e = c - d

print(a[i])

for e in a[3]:
    print (e)

for i in range(len(a)-1):
    print(a[i])

if e > 0:
    f = e + 1
elif e == 0:
    f = 0
else:
    f = e - 1

g = a ** 2
h = b // 3
i = g + h

a += 5
b -= 2
c *= 3

a = 4
print(a)
b = 5
a = "hola"
b = a + (str(b))
print(b)

# Detener el cronómetro
fin = time.time()
duracion = (fin - inicio) * 1000  # convertir a milisegundos
print(f"\nTiempo de ejecución: {duracion:.4f} milisegundos")