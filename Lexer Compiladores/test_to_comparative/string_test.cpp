#include <iostream>
#include <string>
#include <chrono>

int main() {
    // Iniciar el cronómetro
    auto inicio = std::chrono::high_resolution_clock::now();

    // Inicializando con un literal de cadena
    std::string greeting = "Hello, World!";

    // Inicializada como una cadena vacía
    std::string empty_string = "";

    // Usando sintaxis de inicialización directa
    std::string name = "Alice";

    // Imprimir la cadena
    std::cout << greeting << std::endl;

    // Detener el cronómetro
    auto fin = std::chrono::high_resolution_clock::now();
    
    // Calcular la duración
    auto duracion = std::chrono::duration_cast<std::chrono::microseconds>(fin - inicio);
    
    std::cout << "\nTiempo de ejecución: " << duracion.count() << " microsegundos" << std::endl;
    std::cout << "Tiempo de ejecución: " << duracion.count() / 1000.0 << " milisegundos" << std::endl;

    return 0;
}