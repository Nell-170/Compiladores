<<<<<<< Updated upstream
#include "PyObject.hpp"   // o "../pyobject.hpp" según tu estructura
#include <chrono>
#include <iostream>
#include <map>
#include <vector>
=======
#include <chrono>
#include <iostream>

#include "../pyobject.hpp"
>>>>>>> Stashed changes

using std::cout;
using std::endl;

// Sumar dos PyObject sin copias innecesarias
PyObject hola(const PyObject& a, const PyObject& b) {
    return a + b;
}

<<<<<<< Updated upstream
// Fibonacci iterativo mucho más eficiente
PyObject fib(const PyObject& n_obj) {
    const long long n = n_obj.to_int();

    if (n <= 0) {
        return PyObject(0);
    }
    if (n == 1 || n == 2) {
        return PyObject(1);
=======
// Fibonacci with proper base cases
PyObject fib(PyObject n) {
  if ((n <= 0)()) {
    return 0;
  }
    if ((n == 1)() || (n == 2)()) {
      return 1;
>>>>>>> Stashed changes
    }

    long long prev = 1;
    long long curr = 1;

    for (long long i = 3; i <= n; ++i) {
        const long long next = prev + curr;
        prev = curr;
        curr = next;
    }

    return PyObject(curr);
}

int main() {
    using Clock = std::chrono::high_resolution_clock;

    // Iniciar el cronómetro
    const auto inicio = Clock::now();

    // Operaciones básicas
    cout << hola(1, 2) << '\n';
    cout << fib(5) << '\n';

    PyObject a = 4;
    cout << a << '\n';

    PyObject b = 5;
    a = "hola";
    b = a + PyObject(b.to_string());
    cout << b << '\n';

    // Diccionario
    std::map<PyObject, PyObject, PyObjectCompare> dict_map;
    dict_map.emplace(PyObject("z"), PyObject(1));
    dict_map.emplace(PyObject("x"), PyObject("ECCI"));
    PyObject dict(dict_map);

    // Lista interna
    PyObject inner_list(std::vector<PyObject>{1, 2, 3, 4});

    // "Tupla" (en runtime es otra lista)
    PyObject tuple(std::vector<PyObject>{1, 2, 3, 4});
    // Si tienes algo como PyObject::from_tuple(...) y quieres usarlo:
    // PyObject tuple = PyObject::from_tuple(std::vector<PyObject>{1, 2, 3, 4});

    // Lista principal
    a = PyObject(std::vector<PyObject>{1, "hola", dict, inner_list, tuple});
    cout << a << '\n';

    cout << "Fibonacci\n";

    // Bucle sobre a, usando tipos nativos y evitando conversions repetidas
    const auto len_a = len(a);  // asumo que len(a) devuelve algo tipo size_t o int
    for (size_t i = 0; i + 1 < static_cast<size_t>(len_a); ++i) {
        cout << a[PyObject(static_cast<long long>(i))] << '\n';
    }

    // Iterar sobre a[3] = [1, 2, 3, 4], evitando copias
    PyObject a3 = a[PyObject(3)];
    for (const auto& e : a3.get_list()) {
        cout << e << '\n';
    }

    // Bucle con comparación entre enteros, manteniendo la lógica original
    a = 5;
    b = 10;
    while (a < b) {
        cout << fib(b - 5) << '\n';
        PyObject c = b;

        // Esto solo demuestra que puedes cambiar de tipo;
        // si quisieras máximo rendimiento podrías quitar esta línea.
        b = "hola";

        b = c - 2;
    }

<<<<<<< Updated upstream
    cout << "Si printeo mis probabilidades de graduarme suben :)\n";
=======
    // Comparisons
    if ((a < b)()) {
      std::cout << "4 < 5" << std::endl;  // Should print this
    }

    // While loop
    PyObject counter = 0;
    while ((counter < 3)) {
      std::cout << counter << std::endl;  // Should print: 0 1 2
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
>>>>>>> Stashed changes

    // Detener el cronómetro
    const auto fin = Clock::now();

    // Calcular la duración
    const auto duracion =
        std::chrono::duration_cast<std::chrono::microseconds>(fin - inicio);

    cout << "\nTiempo de ejecucion: " << duracion.count() << " microsegundos\n";
    cout << "Tiempo de ejecucion: " << duracion.count() / 1000.0
         << " milisegundos\n";

    return 0;
}