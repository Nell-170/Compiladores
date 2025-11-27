#include <iostream>
#include <map>
#include <tuple>
#include <vector>

#include "PyObject.hpp"
using namespace std;

PyObject add(PyObject a, PyObject b) { return (a + b); }
PyObject fib(PyObject n) {
  if ((n <= 0)) {
    return PyObject(0);
  }
  if (((n == 1) || (n == 2))) {
    return PyObject(1);
  }
  return (fib((n - 1)) + fib((n - 2)));
}
int main() {
  PyObject a = vector<PyObject>{1, 2, 3};
  cout << a << endl;
  cout << a[0] << endl;
  cout << a[1] << endl;
  cout << len(a) << endl;
  for (auto i : (a).get_list()) {
    cout << i << endl;
  }
  PyObject b = vector<PyObject>{"hola", "mundo"};
  cout << b << endl;
  PyObject empty = vector<PyObject>{};
  if (!(empty).to_bool()) {
    cout << "Lista vac\u00eda es falsy" << endl;
  }
  if ((a < b)) {
    cout << "4 < 5" << endl;
  }
  PyObject counter = 0;
  while ((counter < 3)) {
    cout << counter << endl;
    counter = (counter + 1);
  }
  cout << "All tests passed!" << endl;
  return 0;
}
