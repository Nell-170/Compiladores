#include <iostream>
#include <set>
#include <string>
#include <chrono>

int main() {
    // Iniciar el cronómetro
    auto inicio = std::chrono::high_resolution_clock::now();

    // set básico
    std::set<std::string> materias = {"Compiladores", "IA"};

    // "agregar" (parecido a append)
    materias.insert("Analisis Numerico");
    materias.insert("IA");  // no se repite, porque el set es único

    // no hay sublist/slice en set (porque no hay orden)

    // "remove" pero del elemento (no por índice)
    materias.erase("IA");

    // imprimir el set
    std::cout << "{";
    for (auto it = materias.begin(); it != materias.end(); ++it) {
        if (it != materias.begin()) std::cout << ", ";
        std::cout << "'" << *it << "'";
    }
    std::cout << "}" << std::endl;  // {'Analisis Numerico', 'Compiladores'}

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
