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
    if ((n <= 0)) {
        return PyObject(0);
    }
    if ((py_or((n == 1), (n == 2))).to_bool()) {
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
    if (!(empty).to_bool()) {
        cout << "Empty string is falsy" << endl;
    }
    if ((a < b)) {
    if ((a < b)) {
        cout << "4 < 5" << endl;
    }
    PyObject counter = 0;
    while ((counter < 3)) {
    while ((counter < 3)) {
        cout << counter << endl;
        counter = (counter + 1);
    }
    cout << "=== Testing 'and' operator ===" << endl;
    PyObject result1 = py_and(5, 10);
    cout << result1 << endl;
    PyObject result2 = py_and(0, 10);
    cout << result2 << endl;
    PyObject result3 = py_and(5, 0);
    cout << result3 << endl;
    PyObject result4 = py_and("", "hello");
    cout << result4 << endl;
    PyObject result5 = py_and("hello", "world");
    cout << result5 << endl;
    cout << "" << endl;
    cout << "=== Testing 'or' operator ===" << endl;
    PyObject result6 = py_or(5, 10);
    cout << result6 << endl;
    PyObject result7 = py_or(0, 10);
    cout << result7 << endl;
    PyObject result8 = py_or(0, 0);
    cout << result8 << endl;
    PyObject result9 = py_or("", "hello");
    cout << result9 << endl;
    PyObject result10 = py_or("hello", "world");
    cout << result10 << endl;
    cout << "" << endl;
    cout << "=== Testing in conditionals ===" << endl;
    if ((py_and(5, 10)).to_bool()) {
        cout << "5 and 10 is truthy" << endl;
    }
    if ((py_and(0, 10)).to_bool()) {
        cout << "0 and 10 is truthy" << endl;
    } else {
        cout << "0 and 10 is falsy" << endl;
    }
    if ((py_or(5, 0)).to_bool()) {
        cout << "5 or 0 is truthy" << endl;
    }
    if ((py_or(0, "")).to_bool()) {
        cout << "0 or empty string is truthy" << endl;
    } else {
        cout << "0 or empty string is falsy" << endl;
    }
    cout << "" << endl;
    cout << "=== Testing chained and/or ===" << endl;
    PyObject result11 = py_and(py_and(1, 2), 3);
    cout << result11 << endl;
    PyObject result12 = py_and(py_and(1, 0), 3);
    cout << result12 << endl;
    PyObject result13 = py_or(py_or(0, 0), 5);
    cout << result13 << endl;
    PyObject result14 = py_or(py_or(1, 2), 3);
    cout << result14 << endl;
    cout << "" << endl;
    cout << "=== Testing with different types ===" << endl;
    PyObject result15 = py_and(42, "hello");
    cout << result15 << endl;
    PyObject result16 = py_or("", 42);
    cout << result16 << endl;
    PyObject result17 = py_and("hello", 123);
    cout << result17 << endl;
    cout << "" << endl;
    cout << "All and/or tests complete!" << endl;
    cout << "All tests passed!" << endl;
    return 0;
}