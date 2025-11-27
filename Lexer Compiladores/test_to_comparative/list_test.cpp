#include <iostream>
#include <vector>
#include <chrono>

int main() {
    // Iniciar el cronómetro
    auto inicio = std::chrono::high_resolution_clock::now();

    // lista básica
    std::vector<int> numeros = {1, 2, 3};

    // append - agregar elemento al final
    numeros.push_back(4);
    numeros.push_back(5);

    // imprimir
    std::cout << "[";
    for (size_t i = 0; i < numeros.size(); ++i) {
        if (i > 0) std::cout << ", ";
        std::cout << numeros[i];
    }
    std::cout << "]" << std::endl;  // [1, 2, 3, 4, 5]

    // sublist (slicing) - obtener sublista
    std::vector<int> sub(numeros.begin() + 1, numeros.begin() + 4);
    std::cout << "[";
    for (size_t i = 0; i < sub.size(); ++i) {
        if (i > 0) std::cout << ", ";
        std::cout << sub[i];
    }
    std::cout << "]" << std::endl;  // [2, 3, 4]

    // remove por index usando erase (equivalente a del)
    numeros.erase(numeros.begin() + 0);
    std::cout << "[";
    for (size_t i = 0; i < numeros.size(); ++i) {
        if (i > 0) std::cout << ", ";
        std::cout << numeros[i];
    }
    std::cout << "]" << std::endl;  // [2, 3, 4, 5]

    // remove por index (equivalente a pop)
    numeros.erase(numeros.begin() + 2);
    std::cout << "[";
    for (size_t i = 0; i < numeros.size(); ++i) {
        if (i > 0) std::cout << ", ";
        std::cout << numeros[i];
    }
    std::cout << "]" << std::endl;  // [2, 3, 5]

    // Detener el cronómetro
    auto fin = std::chrono::high_resolution_clock::now();
    
    // Calcular la duración
    auto duracion = std::chrono::duration_cast<std::chrono::microseconds>(fin - inicio);
    
    std::cout << "\nTiempo de ejecución: " << duracion.count() << " microsegundos" << std::endl;
    std::cout << "Tiempo de ejecución: " << duracion.count() / 1000.0 << " milisegundos" << std::endl;

    return 0;
}