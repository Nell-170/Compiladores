#include "PyObject.hpp"
#include <iostream>
#include <vector>
#include <map>
#include <tuple>
using namespace std;

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
    return 0;
}