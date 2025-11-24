#include <iostream>
#include <string>
#include <vector>
#include <map>
using namespace std;

int hola(int ['a'].b) {
    return (a + b);
}
int fib(int n) {
    if (((n == 1) || (n == 2))) {
        return 1;
    } else {
        return (fib((n - 1)) + fib((n - 2)));
    }
}
int main() {
    cout << hola(1, 2) << endl;
    cout << fib(5) << endl;
    ssize_t a = 4;
    cout << a << endl;
    ssize_t b = 5;
    string a = "hola";
    string b = (a + (to_string(b)));
    cout << b << endl;
    vector<int> a = vector<ssize_t>{1, "hola", map<string, ssize_t>{{"z", 1}, {"x", "ECCI"}}, vector<ssize_t>{1, 2, 3, 4}, make_tuple(1, 2, 3, 4)};
    cout << a << endl;
    cout << "Fibonacci" << endl;
    for (ssize_t i = 0; i < ((a).size() - 1); i++) {
        cout << a[i] << endl;
    }
    for (auto e : a[3]) {
        cout << e << endl;
        ssize_t a = 5;
    }
    ssize_t b = 10;
    while ((a < b)) {
        cout << fib((b - 5)) << endl;
        ssize_t c = b;
        string b = "hola";
        ssize_t b = (c - 2);
    }
    cout << "Si printeo mis probabilidades de graduarme suben :)" << endl;
    return 0;
}