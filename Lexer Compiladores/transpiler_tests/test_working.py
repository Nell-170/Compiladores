import time

# Iniciar el cronómetro
inicio = time.time()

# This test file contains VALID Python code that should transpile and run correctly

# Function with proper return types
def add(a, b):
    return a + b

print(add(1, 2))        # Should print: 3
print(add("hello", "world"))  # Should print: helloworld

# Fibonacci with proper base cases
def fib(n):
    if n <= 0:
        return 0
    if n == 1 or n == 2:
        return 1
    return fib(n-1) + fib(n-2)

print(fib(5))           # Should print: 5

# String operations
s = "hello"
print(s)                # Should print: hello
print(len(s))           # Should print: 5
print(s[0])             # Should print: h
print(s * 2)            # Should print: hellohello

# Type changes
x = 42
print(x)                # Should print: 42

x = "world"
print(x)                # Should print: world

x = 3.14
print(x)                # Should print: 3.14

# String concatenation with type conversion
a = 4
b = 5
result = str(a) + str(b)
print(result)           # Should print: 45

# Loops
print("Loop test:")
for i in range(5):
    print(i)            # Should print: 0 1 2 3 4

# String truthiness
if s:
    print("String is truthy")  # Should print this

empty = ""
if not empty:
    print("Empty string is falsy")  # Should print this

# Comparisons
if a < b:
    print("4 < 5")      # Should print this

# While loop
counter = 0
while counter < 3:
    print(counter)      # Should print: 0 1 2
    counter = counter + 1

# Test Python and/or semantics - they return operands, not booleans!

print("=== Testing 'and' operator ===")

# and returns the first falsy value, or the last value if all truthy
result1 = 5 and 10
print(result1)  # Should print: 10

result2 = 0 and 10
print(result2)  # Should print: 0

result3 = 5 and 0
print(result3)  # Should print: 0

result4 = "" and "hello"
print(result4)  # Should print: (empty string)

result5 = "hello" and "world"
print(result5)  # Should print: world

print("")
print("=== Testing 'or' operator ===")

# or returns the first truthy value, or the last value if all falsy
result6 = 5 or 10
print(result6)  # Should print: 5

result7 = 0 or 10
print(result7)  # Should print: 10

result8 = 0 or 0
print(result8)  # Should print: 0

result9 = "" or "hello"
print(result9)  # Should print: hello

result10 = "hello" or "world"
print(result10)  # Should print: hello

print("")
print("=== Testing in conditionals ===")

# In conditionals, the result is still converted to bool
if 5 and 10:
    print("5 and 10 is truthy")  # Should print this

if 0 and 10:
    print("0 and 10 is truthy")  # Should NOT print
else:
    print("0 and 10 is falsy")  # Should print this

if 5 or 0:
    print("5 or 0 is truthy")  # Should print this

if 0 or "":
    print("0 or empty string is truthy")  # Should NOT print
else:
    print("0 or empty string is falsy")  # Should print this

print("")
print("=== Testing chained and/or ===")

result11 = 1 and 2 and 3
print(result11)  # Should print: 3

result12 = 1 and 0 and 3
print(result12)  # Should print: 0

result13 = 0 or 0 or 5
print(result13)  # Should print: 5

result14 = 1 or 2 or 3
print(result14)  # Should print: 1

print("")
print("=== Testing with different types ===")

result15 = 42 and "hello"
print(result15)  # Should print: hello

result16 = "" or 42
print(result16)  # Should print: 42

result17 = "hello" and 123
print(result17)  # Should print: 123

print("")
print("All and/or tests complete!")

print("All tests passed!")

# Detener el cronómetro
fin = time.time()
duracion = (fin - inicio) * 1000  # convertir a milisegundos
print(f"\nTiempo de ejecucion: {duracion:.4f} milisegundos")
