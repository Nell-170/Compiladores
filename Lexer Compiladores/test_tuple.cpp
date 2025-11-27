#include "PyObject.hpp"
#include <iostream>
using namespace std;

int main() {
    // Create a list with a tuple
    vector<PyObject> inner = {1, 2, 3, 4};
    PyObject tup = PyObject::from_tuple(inner);
    
    cout << "Tuple: " << tup << endl;
    
    vector<PyObject> outer_vec = {1, "hello", tup};
    PyObject list = PyObject(outer_vec);
    
    cout << "List: " << list << endl;
    
    // Try to access and print
    cout << "Element 2: " << list[2] << endl;
    
    // Try to iterate
    for (auto e : list[2].get_list()) {
        cout << "Item from tuple: " << e << endl;
    }
    
    // Try to assign something new
    list = 5;
    cout << "After assignment: " << list << endl;
    
    return 0;
}
