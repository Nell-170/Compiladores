import time

# Iniciar el cronómetro
inicio = time.time()

# Inicializando con un literal de cadena (similar a std::string greeting)
greeting = "Hello, World!"

# Inicializada como una cadena vacía (similar a std::string emptyString)
empty_string = ""

# Usando sintaxis de inicialización directa (similar a std::string name("Alice"))
# Aunque puedes usar str("Alice"), es más común y directo simplemente asignar el literal.
name = "Alice"

# Imprimir la cadena (similar a std::cout << greeting << std::endl;)
print(greeting)

# En Python, el programa termina automáticamente sin necesidad de 'return 0'

# Detener el cronómetro
fin = time.time()
duracion = (fin - inicio) * 1000  # convertir a milisegundos
print(f"\nTiempo de ejecucion: {duracion:.4f} milisegundos")
