#include "PyObject.hpp"
#include <iostream>
#include <vector>
#include <map>
#include <tuple>
using namespace std;

PyObject add(PyObject a, PyObject b) {
    return (a + b);
}
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
    cout << add(1, 2) << endl;
    cout << add("hello", "world") << endl;
    cout << fib(5) << endl;
    PyObject s = "hello";
    cout << s << endl;
    cout << len(s) << endl;
    cout << s[0] << endl;
    cout << (s * 2) << endl;
    PyObject x = 42;
    cout << x << endl;
    x = "world";
    cout << x << endl;
    x = 3.14;
    cout << x << endl;
    PyObject a = 4;
    PyObject b = 5;
    PyObject result = ((a).to_string() + (b).to_string());
    cout << result << endl;
    cout << "Loop test:" << endl;
    for (PyObject i = 0; (i).to_int() < PyObject(5).to_int(); i = PyObject((i).to_int() + 1)) {
        cout << i << endl;
    }
    if ((s).to_bool()) {
        cout << "String is truthy" << endl;
    }
    PyObject empty = "";
    if (!(empty).to_bool()) {
        cout << "Empty string is falsy" << endl;
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