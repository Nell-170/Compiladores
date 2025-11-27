#include <iostream>
#include <chrono>
#include "pyobject.h"

int main() {
    // Iniciar el cronómetro
    auto inicio = std::chrono::high_resolution_clock::now();

    PyObject a = 5;
    PyObject b = 10;
    PyObject c = a + b;

    PyObject d;
    if ((a < b).to_bool()) {
        d = a * 2;
    } else {
        d = b * 2;
    }

    PyObject e = c - d;

    // Crear una lista para los loops
    PyObject a_lista = PyObject(std::vector<PyObject>{1, 2, 3, 4, 5});

    // print(a[i]) - usando la lista
    PyObject i = 0;
    std::cout << a_lista[i] << std::endl;

    // for e in a[3]: - a[3] sería un elemento, no iterable
    // Lo omito porque no tiene sentido iterar sobre un entero

    // for i in range(len(a)-1):
    for (size_t idx = 0; idx < len(a_lista) - 1; ++idx) {
        std::cout << a_lista[PyObject((long long)idx)] << std::endl;
    }

    PyObject f;
    if ((e > 0).to_bool()) {
        f = e + 1;
    } else if ((e == 0).to_bool()) {
        f = 0;
    } else {
        f = e - 1;
    }

    PyObject g = py_pow(a, 2);
    PyObject h = floor_div(b, 3);
    i = g + h;

    a = a + 5;
    b = b - 2;
    c = c * 3;

    a = 4;
    std::cout << a << std::endl;
    b = 5;
    a = "hola";
    b = a + PyObject(b.to_string());
    std::cout << b << std::endl;

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
