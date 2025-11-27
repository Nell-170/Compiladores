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
    
    PyObject edades = PyObject(std::map<PyObject, PyObject, PyObjectCompare>{{"Ana", 20}, {"Luis", 22}});
    edades["Milton"] = 21;
    edades["Ana"] = 21;
    cout << edades["Luis"] << endl;
    cout << edades << endl;
    
    // Detener el cronómetro
    auto fin = std::chrono::high_resolution_clock::now();
    
    // Calcular la duración
    auto duracion = std::chrono::duration_cast<std::chrono::microseconds>(fin - inicio);
    
    cout << "\nTiempo de ejecucion: " << duracion.count() << " microsegundos" << endl;
    cout << "Tiempo de ejecucion: " << duracion.count() / 1000.0 << " milisegundos" << endl;
    return 0;
}