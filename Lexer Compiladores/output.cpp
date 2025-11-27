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
    
    PyObject numeros = PyObject(std::vector<PyObject>{1, 2, 3});
    numeros.append(4);
    numeros.append(5);
    cout << numeros << endl;
    PyObject sub = (numeros).slice((1), (4), true, true);
    cout << sub << endl;
    cout << numeros << endl;
    cout << numeros << endl;
    
    // Detener el cronómetro
    auto fin = std::chrono::high_resolution_clock::now();
    
    // Calcular la duración
    auto duracion = std::chrono::duration_cast<std::chrono::microseconds>(fin - inicio);
    
    cout << "\nTiempo de ejecucion: " << duracion.count() << " microsegundos" << endl;
    cout << "Tiempo de ejecucion: " << duracion.count() / 1000.0 << " milisegundos" << endl;
    return 0;
}