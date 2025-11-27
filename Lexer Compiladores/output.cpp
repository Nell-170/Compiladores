#include "PyObject.hpp"
#include <iostream>
#include <vector>
#include <map>
#include <tuple>
#include <chrono>
using namespace std;

int main() {
    // Iniciar el cronómetro
    auto inicio = std::chrono::high_resolution_clock::now();
    
    PyObject a = 5;
    PyObject b = 10;
    PyObject c = (a + b);
    if ((a < b)) {
        PyObject d = (a * 2);
    } else {
        d = (b * 2);
    }
    PyObject e = (c - d);
    for (auto e : ((static_cast<const PyObject&>(a))[3]).get_list()) {
        cout << e << endl;
    }
    for (PyObject i = 0; (i).to_int() < PyObject((len(a) - 1)).to_int(); i = PyObject((i).to_int() + 1)) {
        cout << (static_cast<const PyObject&>(a))[i] << endl;
    }
    if ((e > 0)) {
        PyObject f = (e + 1);
    } else if ((e == 0)) {
        f = 0;
    } else {
        f = (e - 1);
    }
    PyObject g = py_pow(a, 2);
    PyObject h = floor_div(b, 3);
    PyObject i = (g + h);
    a = a + 5;
    b = b - 2;
    c = c * 3;
    a = 4;
    cout << a << endl;
    b = 5;
    a = "hola";
    b = (a + (PyObject((b).to_string())));
    cout << b << endl;
    
    // Detener el cronómetro
    auto fin = std::chrono::high_resolution_clock::now();
    
    // Calcular la duración
    auto duracion = std::chrono::duration_cast<std::chrono::microseconds>(fin - inicio);
    
    cout << "\nTiempo de ejecucion: " << duracion.count() << " microsegundos" << endl;
    cout << "Tiempo de ejecucion: " << duracion.count() / 1000.0 << " milisegundos" << endl;
    return 0;
}