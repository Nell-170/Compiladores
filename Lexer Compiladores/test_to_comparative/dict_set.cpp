#include <iostream>
#include <map>
#include <string>
#include <chrono>

int main() {
    // Iniciar el cronómetro
    auto inicio = std::chrono::high_resolution_clock::now();

    // diccionario básico (usando std::map)
    std::map<std::string, int> edades;
    edades["Ana"] = 20;
    edades["Luis"] = 22; // 😠 Emmanuel también estuvo aquí

    // "agregar" (equivalente a append en espíritu)
    edades["Milton"] = 21;  // mete una nueva clave-valor
    edades["Ana"] = 21;     // actualiza una clave existente

    // acceder
    std::cout << edades["Luis"] << std::endl;  // 22

    // no hay sublist/slice en dict

    // "remove" pero por clave (no por índice)
    edades.erase("Luis");

    // imprimir el diccionario
    std::cout << "{";
    for (auto it = edades.begin(); it != edades.end(); ++it) {
        if (it != edades.begin()) std::cout << ", ";
        std::cout << "'" << it->first << "': " << it->second;
    }
    std::cout << "}" << std::endl;  // {'Ana': 21, 'Milton': 21}

    // Detener el cronómetro
    auto fin = std::chrono::high_resolution_clock::now();
    
    // Calcular la duración
    auto duracion = std::chrono::duration_cast<std::chrono::microseconds>(fin - inicio);
    
    std::cout << "\nTiempo de ejecución: " << duracion.count() << " microsegundos" << std::endl;
    std::cout << "Tiempo de ejecución: " << duracion.count() / 1000.0 << " milisegundos" << std::endl;

    return 0;
}