#include <chrono>
#include <iostream>

#include "../pyobject.hpp"

PyObject hola(PyObject a, PyObject b) { return a + b; }

PyObject fib(PyObject n) {
  if ((n == 1) || (n == 2)) {
    return 1;
  } else {
    return fib(n - 1) + fib(n - 2);
  }
}

int main() {
  // Iniciar el cronómetro
  auto inicio = std::chrono::high_resolution_clock::now();

  std::cout << hola(1, 2) << std::endl;

  std::cout << fib(5) << std::endl;

  PyObject a = 4;
  std::cout << a << std::endl;
  PyObject b = 5;
  a = "hola";
  b = a + PyObject(b.to_string());
  std::cout << b << std::endl;

  // Crear el diccionario
  std::map<PyObject, PyObject, PyObjectCompare> dict_map;
  dict_map[PyObject("z")] = PyObject(1);
  dict_map[PyObject("x")] = PyObject("ECCI");
  PyObject dict = PyObject(dict_map);

  // Crear la lista interna
  PyObject inner_list = PyObject(std::vector<PyObject>{1, 2, 3, 4});

  // Crear la tupla (usando vector, ya que PyObject no distingue en runtime)
  PyObject tuple = PyObject(std::vector<PyObject>{1, 2, 3, 4});

  // Crear la lista principal
  a = PyObject(std::vector<PyObject>{1, "hola", dict, inner_list, tuple});
  std::cout << a << std::endl;
  std::cout << "Fibonacci" << std::endl;

  for (size_t i = 0; i < len(a) - 1; ++i) {
    std::cout << a[PyObject((long long)i)] << std::endl;
  }

  // Iterar sobre a[3] que es la lista [1,2,3,4]
  PyObject a3 = a[PyObject(3)];
  for (const auto& e : a3.get_list()) {
    std::cout << e << std::endl;
  }

  a = 5;
  b = 10;
  while ((a < b)) {
    std::cout << fib(b - 5) << std::endl;
    PyObject c = b;
    b = "hola";
    b = c - 2;
  }
  std::cout << "Si printeo mis probabilidades de graduarme suben :)"
            << std::endl;

  // Detener el cronómetro
  auto fin = std::chrono::high_resolution_clock::now();

  // Calcular la duración
  auto duracion =
      std::chrono::duration_cast<std::chrono::microseconds>(fin - inicio);

  std::cout << "\nTiempo de ejecucion: " << duracion.count() << " microsegundos"
            << std::endl;
  std::cout << "Tiempo de ejecucion: " << duracion.count() / 1000.0
            << " milisegundos" << std::endl;

  return 0;
}
