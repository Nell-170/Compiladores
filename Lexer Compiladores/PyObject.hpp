#ifndef PYOBJECT_H
#define PYOBJECT_H

#include <variant>
#include <string>
#include <iostream>
#include <cmath>
#include <stdexcept>
#include <vector>
#include <map>

enum class PyType {
    None,
    Int,
    Float,
    Bool,
    String
};

class PyObject {
private:
    PyType type;
    std::variant<std::monostate, long long, double, bool, /*std::ssize_t,*/ std::string> value;

public:
    // Constructors
    PyObject() : type(PyType::None), value(std::monostate{}) {}
    
    PyObject(int v) : type(PyType::Int), value(static_cast<long long>(v)) {}
    PyObject(long long v) : type(PyType::Int), value(v) {}
    PyObject(double v) : type(PyType::Float), value(v) {}
    PyObject(bool v) : type(PyType::Bool), value(v) {}
    PyObject(const char* v) : type(PyType::String), value(std::string(v)) {}
    PyObject(const std::string& v) : type(PyType::String), value(v) {}

    // Type checking
    PyType get_type() const { return type; }
    bool is_none() const { return type == PyType::None; }
    bool is_int() const { return type == PyType::Int; }
    bool is_float() const { return type == PyType::Float; }
    bool is_bool() const { return type == PyType::Bool; }
    bool is_string() const { return type == PyType::String; }

    // Conversion to bool (Python truthiness)
    bool to_bool() const {
        switch (type) {
            case PyType::None: return false;
            case PyType::Int: return std::get<long long>(value) != 0;
            case PyType::Float: return std::get<double>(value) != 0.0;
            case PyType::Bool: return std::get<bool>(value);
            case PyType::String: return !std::get<std::string>(value).empty();
        }
        return false;
    }

    // Explicit conversion operators
    explicit operator bool() const { return to_bool(); }
    
    long long to_int() const {
        switch (type) {
            case PyType::Int: return std::get<long long>(value);
            case PyType::Float: return static_cast<long long>(std::get<double>(value));
            case PyType::Bool: return std::get<bool>(value) ? 1 : 0;
            case PyType::String: return std::stoll(std::get<std::string>(value));
            default: throw std::runtime_error("Cannot convert to int");
        }
    }

    double to_float() const {
        switch (type) {
            case PyType::Int: return static_cast<double>(std::get<long long>(value));
            case PyType::Float: return std::get<double>(value);
            case PyType::Bool: return std::get<bool>(value) ? 1.0 : 0.0;
            case PyType::String: return std::stod(std::get<std::string>(value));
            default: throw std::runtime_error("Cannot convert to float");
        }
    }

    std::string to_string() const {
        switch (type) {
            case PyType::None: return "None";
            case PyType::Int: return std::to_string(std::get<long long>(value));
            case PyType::Float: return std::to_string(std::get<double>(value));
            case PyType::Bool: return std::get<bool>(value) ? "True" : "False";
            case PyType::String: return std::get<std::string>(value);
        }
        return "";
    }

    // Length (for strings, lists, etc.)
    size_t size() const {
        if (type == PyType::String) {
            return std::get<std::string>(value).size();
        }
        throw std::runtime_error("TypeError: object of type '" + type_name() + "' has no len()");
    }

    // Indexing support (for strings)
    PyObject operator[](const PyObject& index) const {
        if (type == PyType::String) {
            long long idx = index.to_int();
            const std::string& s = std::get<std::string>(value);
            long long size = static_cast<long long>(s.size());
            
            // Handle Python-style negative indexing
            if (idx < 0) {
                idx += size;
            }
            
            // Bounds check with signed index
            if (idx < 0 || idx >= size) {
                throw std::runtime_error("IndexError: string index out of range");
            }
            return PyObject(std::string(1, s[static_cast<size_t>(idx)]));
        }
        throw std::runtime_error("TypeError: '" + type_name() + "' object is not subscriptable");
    }

    // Helper to get type name for error messages
    std::string type_name() const {
        switch (type) {
            case PyType::None: return "NoneType";
            case PyType::Int: return "int";
            case PyType::Float: return "float";
            case PyType::Bool: return "bool";
            case PyType::String: return "str";
        }
        return "unknown";
    }

    // Arithmetic operators
    PyObject operator+(const PyObject& other) const {
        // String concatenation
        if (type == PyType::String || other.type == PyType::String) {
            return PyObject(to_string() + other.to_string());
        }
        // Numeric addition
        if (type == PyType::Float || other.type == PyType::Float) {
            return PyObject(to_float() + other.to_float());
        }
        return PyObject(to_int() + other.to_int());
    }

    PyObject operator-(const PyObject& other) const {
        if (type == PyType::Float || other.type == PyType::Float) {
            return PyObject(to_float() - other.to_float());
        }
        return PyObject(to_int() - other.to_int());
    }

    PyObject operator*(const PyObject& other) const {
        // String repetition
        if (type == PyType::String && other.is_int()) {
            std::string result;
            long long count = other.to_int();
            for (long long i = 0; i < count; i++) {
                result += std::get<std::string>(value);
            }
            return PyObject(result);
        }
        if (is_int() && other.type == PyType::String) {
            std::string result;
            long long count = to_int();
            for (long long i = 0; i < count; i++) {
                result += std::get<std::string>(other.value);
            }
            return PyObject(result);
        }
        // Numeric multiplication
        if (type == PyType::Float || other.type == PyType::Float) {
            return PyObject(to_float() * other.to_float());
        }
        return PyObject(to_int() * other.to_int());
    }

    PyObject operator/(const PyObject& other) const {
        // Always returns float in Python 3
        double divisor = other.to_float();
        if (divisor == 0.0) {
            throw std::runtime_error("ZeroDivisionError: float division");
        }
        return PyObject(to_float() / divisor);
    }

    PyObject operator%(const PyObject& other) const {
        if (type == PyType::Float || other.type == PyType::Float) {
            double divisor = other.to_float();
            if (divisor == 0.0) {
                throw std::runtime_error("ZeroDivisionError: float modulo");
            }
            return PyObject(std::fmod(to_float(), other.to_float()));
        }
        return PyObject(to_int() % other.to_int());
    }

    // Floor division
    PyObject floor_div(const PyObject& other) const {
        if (type == PyType::Float || other.type == PyType::Float) {
            double divisor = other.to_float();
            if (divisor == 0.0) {
                throw std::runtime_error("ZeroDivisionError: float floor division");
            }
            return PyObject(std::floor(to_float() / other.to_float()));
        }
        long long a = to_int();
        long long b = other.to_int();
        if (b == 0) {
            throw std::runtime_error("ZeroDivisionError: integer floor division");
        }
        long long q = a / b;
        long long r = a % b;
        if ((r != 0) && ((r < 0) != (b < 0))) --q;
        return PyObject(q);
    }

    // Power
    PyObject pow(const PyObject& other) const {
        return PyObject(std::pow(to_float(), other.to_float()));
    }

    // Comparison operators
    bool operator==(const PyObject& other) const {
        if (type != other.type) {
            // Try numeric comparison
            if ((is_int() || is_float()) && (other.is_int() || other.is_float())) {
                return to_float() == other.to_float();
            }
            return false;
        }
        switch (type) {
            case PyType::None: return true;
            case PyType::Int: return std::get<long long>(value) == std::get<long long>(other.value);
            case PyType::Float: return std::get<double>(value) == std::get<double>(other.value);
            case PyType::Bool: return std::get<bool>(value) == std::get<bool>(other.value);
            case PyType::String: return std::get<std::string>(value) == std::get<std::string>(other.value);
        }
        return false;
    }

    bool operator!=(const PyObject& other) const {
        return !(*this == other);
    }

    bool operator<(const PyObject& other) const {
        if ((is_int() || is_float()) && (other.is_int() || other.is_float())) {
            return to_float() < other.to_float();
        }
        if (type == PyType::String && other.type == PyType::String) {
            return std::get<std::string>(value) < std::get<std::string>(other.value);
        }
        throw std::runtime_error("Cannot compare these types");
    }

    bool operator>(const PyObject& other) const {
        return other < *this;
    }

    bool operator<=(const PyObject& other) const {
        return !(other < *this);
    }

    bool operator>=(const PyObject& other) const {
        return !(*this < other);
    }

    // Logical operators (use truthiness)
    bool operator&&(const PyObject& other) const {
        return to_bool() && other.to_bool();
    }

    bool operator||(const PyObject& other) const {
        return to_bool() || other.to_bool();
    }

    bool operator!() const {
        return !to_bool();
    }

    // Unary operators
    PyObject operator-() const {
        if (type == PyType::Float) {
            return PyObject(-std::get<double>(value));
        }
        return PyObject(-to_int());
    }

    PyObject operator+() const {
        return *this;
    }

    // Output operator
    friend std::ostream& operator<<(std::ostream& os, const PyObject& obj) {
        os << obj.to_string();
        return os;
    }
};

// Global floor_div function for compatibility
inline PyObject floor_div(const PyObject& a, const PyObject& b) {
    return a.floor_div(b);
}

// Global pow function
inline PyObject py_pow(const PyObject& a, const PyObject& b) {
    return a.pow(b);
}

// TODO(milton): handle len() for things other than strings
// TODO(milton): once lists/dicts live inside PyObject, this becomes much cleaner and you can just return len({args}).
// Helper for len()
inline size_t len(const PyObject& obj) {
    return obj.size();
}

// Python-faithful and/or operators (return operands, not bool)
inline PyObject py_and(const PyObject& left, const PyObject& right) {
    // Python semantics: if left is falsy, return left; else return right
    if (!left.to_bool()) {
        return left;
    }
    return right;
}

inline PyObject py_or(const PyObject& left, const PyObject& right) {
    // Python semantics: if left is truthy, return left; else return right
    if (left.to_bool()) {
        return left;
    }
    return right;
}

#endif // PYOBJECT_H