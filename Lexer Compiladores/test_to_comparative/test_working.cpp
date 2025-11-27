#include "PyObject.hpp"   // o "../pyobject.hpp" según tu estructura
#include <chrono>
#include <iostream>
#include <map>
#include <vector>

using std::cout;
using std::endl;

// Sumar dos PyObject sin copias innecesarias
PyObject hola(const PyObject& a, const PyObject& b) {
    return a + b;
}

// Fibonacci iterativo mucho más eficiente
PyObject fib(const PyObject& n_obj) {
    const long long n = n_obj.to_int();

    if (n <= 0) {
        return PyObject(0);
    }
    if (n == 1 || n == 2) {
        return PyObject(1);
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

    cout << "Si printeo mis probabilidades de graduarme suben :)\n";

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