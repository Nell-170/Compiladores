# Test PRINT
print()
print(x)
print(a, b, c + 1)

# Test TRY-CATCH
try:
    x = 1 / 0
except ZeroDivisionError:
    print("Division by zero!")

try:
    risky_operation()
except NetworkError:
    print("Network failed")
except:
    print("Unknown error")

for a, b in [(1, 2), (3, 4)]:
    try:
        print(a / b)
    except ZeroDivisionError:
        print("Cannot divide by zero")
