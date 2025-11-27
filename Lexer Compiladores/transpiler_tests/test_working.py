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

print("All tests passed!")