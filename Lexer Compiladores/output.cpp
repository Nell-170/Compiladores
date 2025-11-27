#include "PyObject.hpp"
#include <iostream>
#include <vector>
#include <map>
#include <tuple>
using namespace std;

PyObject hola(PyObject a, PyObject b) {
    return (a + b);
}
PyObject fib(PyObject n) {
    if (((n == 1) || (n == 2))) {
        return PyObject(1);
    } else {
        return (fib((n - 1)) + fib((n - 2)));
    }
}
int main() {
    cout << hola(1, 2) << endl;
    cout << fib(5) << endl;
    PyObject a = 4;
    cout << a << endl;
    PyObject b = 5;
    a = "hola";
    b = (a + ((b).to_string()));
    cout << b << endl;
    a = vector<PyObject>{1, "hola", map<PyObject, PyObject>{{"z", 1}, {"x", "ECCI"}}, vector<PyObject>{1, 2, 3, 4}, make_tuple(1, 2, 3, 4)};
    cout << a << endl;
    cout << "Fibonacci" << endl;
    for (PyObject i = 0; (i).to_int() < PyObject((len(a) - 1)).to_int(); i = PyObject((i).to_int() + 1)) {
        cout << a[i] << endl;
    }
    for (auto e : a[3]) {
        cout << e << endl;
    }
    a = 5;
    b = 10;
    while ((a < b)) {
        cout << fib((b - 5)) << endl;
        PyObject c = b;
        b = "hola";
        b = (c - 2);
    }
    cout << "Si printeo mis probabilidades de graduarme suben :)" << endl;
    return 0;
}