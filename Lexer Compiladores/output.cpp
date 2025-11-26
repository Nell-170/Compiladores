#include <iostream>
#include <string>
#include <vector>
#include <set>
#include <tuple>
#include <cstddef>
using namespace std;

template<typename T>
void print_set(const set<T>& s) {
    cout << "{";
    bool first = true;
    for (const auto& elem : s) {
        if (!first) cout << ", ";
        cout << "\"" << elem << "\"";
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
    return 0;
}