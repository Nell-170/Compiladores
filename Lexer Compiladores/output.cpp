#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <set>
#include <tuple>
using namespace std;

template<typename T>
void print_set(const set<T>& s) {
    cout << "{";
    bool first = true;
    for (const auto& elem : s) {
        if (!first) cout << ", ";
        cout << "\"" << elem << "\"";
        first = false;
#include <cstddef>
using namespace std;

int hola(int a, int b) {
    return (a + b);
}
int fib(int n) {
    if (((n == 1) || (n == 2))) {
        return 1;
    } else {
        return (fib((n - 1)) + fib((n - 2)));
    }
    cout << "}" << endl;
}

template<typename K, typename V>
void print_map(const map<K, V>& m) {
    cout << "{";
    bool first = true;
    for (const auto& pair : m) {
        if (!first) cout << ", ";
        cout << "\"" << pair.first << "\": " << pair.second;
        first = false;
    }
    cout << "}" << endl;
}

int main() {
    set<string> materias = set<string>{"Compiladores", "IA"};
    materias.insert("Analisis Numerico");
    materias.insert("IA");
    materias.erase("IA");
    print_set(materias);
    cout << hola(1, 2) << endl;
    cout << fib(5) << endl;
    ssize_t a = 4;
    cout << a << endl;
    ssize_t b = 5;
    b = (a + (to_string(b)));
    cout << b << endl;
    cout << a << endl;
    cout << "Fibonacci" << endl;
    for (ssize_t i = 0; i < ((a).size() - 1); i++) {
        cout << a[i] << endl;
    }
    for (auto e : a[3]) {
        cout << e << endl;
        a = 5;
    }
    b = 10;
    while ((a < b)) {
        cout << fib((b - 5)) << endl;
        ssize_t c = b;
        string b = "hola";
        ssize_t b = (c - 2);
    }
    cout << "Si printeo mis probabilidades de graduarme suben :)" << endl;
    return 0;
}