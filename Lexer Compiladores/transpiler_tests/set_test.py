import time

# Iniciar el cronómetro
inicio = time.time()

# set básico
materias = {"Compiladores", "IA"}

# "agregar" (parecido a append)
materias.add("Analisis Numerico")
materias.add("IA")  # no se repite, porque el set es único

# no hay sublist/slice en set (porque no hay orden)

# "remove" pero del elemento (no por índice)
materias.remove("IA")

print(materias)  # {'Compiladores', 'Análisis Numérico'}

# Detener el cronómetro
fin = time.time()
duracion = (fin - inicio) * 1000  # convertir a milisegundos
print(f"\nTiempo de ejecución: {duracion:.4f} milisegundos")
