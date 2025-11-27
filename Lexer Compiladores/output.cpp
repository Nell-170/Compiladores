#include "PyObject.hpp"
#include <iostream>
#include <vector>
#include <unordered_map>
#include <tuple>
using namespace std;

int main() {
    PyObject a = 5;
    PyObject b = 10;
    PyObject c = 15;
    PyObject __tmp_1 = 10;
    PyObject __tmp_2 = 15;
    if (((5 < __tmp_1) && (__tmp_1 < __tmp_2))) {
        cout << "yes" << endl;
    } else {
        cout << "no" << endl;
    }
    PyObject __tmp_3 = b;
    PyObject __tmp_4 = c;
    if (((a < __tmp_3) && (__tmp_3 < __tmp_4))) {
        cout << "a < b < c" << endl;
    }
    PyObject __tmp_5 = 2;
    PyObject __tmp_6 = 3;
    PyObject __tmp_7 = 4;
    if (((1 < __tmp_5) && (__tmp_5 < __tmp_6) && (__tmp_6 < __tmp_7))) {
        cout << "1 < 2 < 3 < 4" << endl;
    }
    return 0;
}