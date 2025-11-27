#include <iostream>
#include <chrono>
#include "pyobject.h"

// Function with proper return types
PyObject add(PyObject a, PyObject b) {
    return a + b;
}

// Fibonacci with proper base cases
PyObject fib(PyObject n) {
    if ((n <= 0).to_bool()) {
        return 0;
    }
    if ((n == 1).to_bool() || (n == 2).to_bool()) {
        return 1;
    }
    return fib(n - 1) + fib(n - 2);
}

int main() {
    // Iniciar el cronómetro
    auto inicio = std::chrono::high_resolution_clock::now();

    std::cout << add(1, 2) << std::endl;        // Should print: 3
    std::cout << add("hello", "world") << std::endl;  // Should print: helloworld

    std::cout << fib(5) << std::endl;           // Should print: 5

    // String operations
    PyObject s = "hello";
    std::cout << s << std::endl;                // Should print: hello
    std::cout << len(s) << std::endl;           // Should print: 5
    std::cout << s[0] << std::endl;             // Should print: h
    std::cout << s * 2 << std::endl;            // Should print: hellohello

    // Type changes
    PyObject x = 42;
    std::cout << x << std::endl;                // Should print: 42

    x = "world";
    std::cout << x << std::endl;                // Should print: world

    x = 3.14;
    std::cout << x << std::endl;                // Should print: 3.14

    // String concatenation with type conversion
    PyObject a = 4;
    PyObject b = 5;
    PyObject result = PyObject(a.to_string()) + PyObject(b.to_string());
    std::cout << result << std::endl;           // Should print: 45

    // Loops
    std::cout << "Loop test:" << std::endl;
    for (long long i = 0; i < 5; ++i) {
        std::cout << i << std::endl;            // Should print: 0 1 2 3 4
    }

    // String truthiness
    if (s.to_bool()) {
        std::cout << "String is truthy" << std::endl;  // Should print this
    }

    PyObject empty = "";
    if (!empty.to_bool()) {
        std::cout << "Empty string is falsy" << std::endl;  // Should print this
    }

    // Comparisons
    if ((a < b).to_bool()) {
        std::cout << "4 < 5" << std::endl;      // Should print this
    }

    // While loop
    PyObject counter = 0;
    while ((counter < 3).to_bool()) {
        std::cout << counter << std::endl;      // Should print: 0 1 2
        counter = counter + 1;
    }

    // Test Python and/or semantics - they return operands, not booleans!

    std::cout << "=== Testing 'and' operator ===" << std::endl;

    // and returns the first falsy value, or the last value if all truthy
    PyObject result1 = py_and(5, 10);
    std::cout << result1 << std::endl;  // Should print: 10

    PyObject result2 = py_and(0, 10);
    std::cout << result2 << std::endl;  // Should print: 0

    PyObject result3 = py_and(5, 0);
    std::cout << result3 << std::endl;  // Should print: 0

    PyObject result4 = py_and("", "hello");
    std::cout << result4 << std::endl;  // Should print: (empty string)

    PyObject result5 = py_and("hello", "world");
    std::cout << result5 << std::endl;  // Should print: world

    std::cout << "" << std::endl;
    std::cout << "=== Testing 'or' operator ===" << std::endl;

    // or returns the first truthy value, or the last value if all falsy
    PyObject result6 = py_or(5, 10);
    std::cout << result6 << std::endl;  // Should print: 5

    PyObject result7 = py_or(0, 10);
    std::cout << result7 << std::endl;  // Should print: 10

    PyObject result8 = py_or(0, 0);
    std::cout << result8 << std::endl;  // Should print: 0

    PyObject result9 = py_or("", "hello");
    std::cout << result9 << std::endl;  // Should print: hello

    PyObject result10 = py_or("hello", "world");
    std::cout << result10 << std::endl;  // Should print: hello

    std::cout << "" << std::endl;
    std::cout << "=== Testing in conditionals ===" << std::endl;

    // In conditionals, the result is still converted to bool
    if (py_and(5, 10).to_bool()) {
        std::cout << "5 and 10 is truthy" << std::endl;  // Should print this
    }

    if (py_and(0, 10).to_bool()) {
        std::cout << "0 and 10 is truthy" << std::endl;  // Should NOT print
    } else {
        std::cout << "0 and 10 is falsy" << std::endl;  // Should print this
    }

    if (py_or(5, 0).to_bool()) {
        std::cout << "5 or 0 is truthy" << std::endl;  // Should print this
    }

    if (py_or(0, "").to_bool()) {
        std::cout << "0 or empty string is truthy" << std::endl;  // Should NOT print
    } else {
        std::cout << "0 or empty string is falsy" << std::endl;  // Should print this
    }

    std::cout << "" << std::endl;
    std::cout << "=== Testing chained and/or ===" << std::endl;

    PyObject result11 = py_and(py_and(1, 2), 3);
    std::cout << result11 << std::endl;  // Should print: 3

    PyObject result12 = py_and(py_and(1, 0), 3);
    std::cout << result12 << std::endl;  // Should print: 0

    PyObject result13 = py_or(py_or(0, 0), 5);
    std::cout << result13 << std::endl;  // Should print: 5

    PyObject result14 = py_or(py_or(1, 2), 3);
    std::cout << result14 << std::endl;  // Should print: 1

    std::cout << "" << std::endl;
    std::cout << "=== Testing with different types ===" << std::endl;

    PyObject result15 = py_and(42, "hello");
    std::cout << result15 << std::endl;  // Should print: hello

    PyObject result16 = py_or("", 42);
    std::cout << result16 << std::endl;  // Should print: 42

    PyObject result17 = py_and("hello", 123);
    std::cout << result17 << std::endl;  // Should print: 123

    std::cout << "" << std::endl;
    std::cout << "All and/or tests complete!" << std::endl;

    std::cout << "All tests passed!" << std::endl;

    // Detener el cronómetro
    auto fin = std::chrono::high_resolution_clock::now();
    
    // Calcular la duración
    auto duracion = std::chrono::duration_cast<std::chrono::microseconds>(fin - inicio);

    std::cout << "\nTiempo de ejecucion: " << duracion.count()
              << " microsegundos" << std::endl;
    std::cout << "Tiempo de ejecucion: " << duracion.count() / 1000.0
              << " milisegundos" << std::endl;

    return 0;
}
