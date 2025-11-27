#ifndef PYOBJECT_H
#define PYOBJECT_H

#include <stddef.h>

#include <cmath>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <variant>
#include <vector>

// Forward declaration for comparator
class PyObject;

// Comparator for PyObject in std::set and std::map
struct PyObjectCompare {
  bool operator()(const PyObject& a, const PyObject& b) const;
};

enum class PyType { None, Int, Float, Bool, String, List, Set, Dict, Tuple };

class PyObject {
 private:
  PyType type;
  std::variant<std::monostate, long long, double, bool, std::string,
               std::vector<PyObject>, std::set<PyObject, PyObjectCompare>,
               std::map<PyObject, PyObject, PyObjectCompare>>
      value;

 public:
  // Constructors
  PyObject() : type(PyType::None), value(std::monostate{}) {}

  PyObject(int v) : type(PyType::Int), value(static_cast<long long>(v)) {}
  PyObject(long long v) : type(PyType::Int), value(v) {}
  PyObject(double v) : type(PyType::Float), value(v) {}
  PyObject(bool v) : type(PyType::Bool), value(v) {}
  PyObject(const char* v) : type(PyType::String), value(std::string(v)) {}
  PyObject(const std::string& v) : type(PyType::String), value(v) {}

  // Constructor for vectors/lists
  PyObject(const std::vector<PyObject>& v) : type(PyType::List), value(v) {}
  PyObject(std::vector<PyObject>&& v)
      : type(PyType::List), value(std::move(v)) {}

  // Constructor for sets
  PyObject(const std::set<PyObject, PyObjectCompare>& v)
      : type(PyType::Set), value(v) {}
  PyObject(std::set<PyObject, PyObjectCompare>&& v)
      : type(PyType::Set), value(std::move(v)) {}

  // Constructor for dicts
  PyObject(const std::map<PyObject, PyObject, PyObjectCompare>& m)
      : type(PyType::Dict), value(m) {}
  PyObject(std::map<PyObject, PyObject, PyObjectCompare>&& m)
      : type(PyType::Dict), value(std::move(m)) {}

  // Type checking
  PyType get_type() const { return type; }
  bool is_none() const { return type == PyType::None; }
  bool is_int() const { return type == PyType::Int; }
  bool is_float() const { return type == PyType::Float; }
  bool is_bool() const { return type == PyType::Bool; }
  bool is_string() const { return type == PyType::String; }
  bool is_list() const { return type == PyType::List; }
  bool is_set() const { return type == PyType::Set; }
  bool is_tuple() const { return type == PyType::Tuple; }
  bool is_dict() const { return type == PyType::Dict; }

  // Conversion to bool (Python truthiness)
  bool to_bool() const {
    switch (type) {
      case PyType::None:
        return false;
      case PyType::Int:
        return std::get<long long>(value) != 0;
      case PyType::Float:
        return std::get<double>(value) != 0.0;
      case PyType::Bool:
        return std::get<bool>(value);
      case PyType::String:
        return !std::get<std::string>(value).empty();
      case PyType::List:
      case PyType::Tuple:
        return !std::get<std::vector<PyObject>>(value).empty();
      case PyType::Set:
        return !std::get<std::set<PyObject, PyObjectCompare>>(value).empty();
      case PyType::Dict:
        return !std::get<std::map<PyObject, PyObject, PyObjectCompare>>(value)
                    .empty();
    }
    return false;
  }

  // Explicit conversion operators
  explicit operator bool() const { return to_bool(); }

  long long to_int() const {
    switch (type) {
      case PyType::Int:
        return std::get<long long>(value);
      case PyType::Float:
        return static_cast<long long>(std::get<double>(value));
      case PyType::Bool:
        return std::get<bool>(value) ? 1 : 0;
      case PyType::String:
        return std::stoll(std::get<std::string>(value));
      default:
        throw std::runtime_error("Cannot convert to int");
    }
  }

  double to_float() const {
    switch (type) {
      case PyType::Int:
        return static_cast<double>(std::get<long long>(value));
      case PyType::Float:
        return std::get<double>(value);
      case PyType::Bool:
        return std::get<bool>(value) ? 1.0 : 0.0;
      case PyType::String:
        return std::stod(std::get<std::string>(value));
      default:
        throw std::runtime_error("Cannot convert to float");
    }
  }

  std::string to_string() const {
    switch (type) {
      case PyType::None:
        return "None";
      case PyType::Int:
        return std::to_string(std::get<long long>(value));
      case PyType::Float:
        return std::to_string(std::get<double>(value));
      case PyType::Bool:
        return std::get<bool>(value) ? "True" : "False";
      case PyType::String:
        return std::get<std::string>(value);
      case PyType::List:
      case PyType::Tuple: {
        const auto& vec = std::get<std::vector<PyObject>>(value);
        std::string result = (type == PyType::Tuple) ? "(" : "[";
        for (size_t i = 0; i < vec.size(); ++i) {
          if (i > 0) result += ", ";
          const auto& elem = vec[i];
          if (elem.is_string()) {
            result += "'" + elem.to_string() + "'";
          } else {
            result += elem.to_string();
          }
        }
        result += (type == PyType::Tuple) ? ")" : "]";
        return result;
      }
      case PyType::Set: {
        const auto& s = std::get<std::set<PyObject, PyObjectCompare>>(value);
        std::string result = "{";
        bool first = true;
        for (const auto& elem : s) {
          if (!first) result += ", ";
          first = false;
          if (elem.is_string()) {
            result += "'" + elem.to_string() + "'";
          } else {
            result += elem.to_string();
          }
        }
        result += "}";
        return result;
      }
      case PyType::Dict: {
        const auto& m =
            std::get<std::map<PyObject, PyObject, PyObjectCompare>>(value);
        std::string result = "{";
        bool first = true;
        for (const auto& [k, v] : m) {
          if (!first) result += ", ";
          first = false;
          if (k.is_string()) {
            result += "'" + k.to_string() + "'";
          } else {
            result += k.to_string();
          }
          result += ": ";
          if (v.is_string()) {
            result += "'" + v.to_string() + "'";
          } else {
            result += v.to_string();
          }
        }
        result += "}";
        return result;
      }
    }
    return "";
  }

  // Length (for strings, lists, sets, dicts, tuples)
  size_t size() const {
    switch (type) {
      case PyType::String:
        return std::get<std::string>(value).size();
      case PyType::List:
      case PyType::Tuple:
        return std::get<std::vector<PyObject>>(value).size();
      case PyType::Set:
        return std::get<std::set<PyObject, PyObjectCompare>>(value).size();
      case PyType::Dict:
        return std::get<std::map<PyObject, PyObject, PyObjectCompare>>(value)
            .size();
      default:
        throw std::runtime_error("TypeError: object of type '" + type_name() +
                                 "' has no len()");
    }
  }

  // Indexing support (for strings, lists, tuples)
  PyObject operator[](const PyObject& index) const {
    long long idx = index.to_int();

    if (type == PyType::String) {
      const std::string& s = std::get<std::string>(value);
      long long sz = static_cast<long long>(s.size());
      if (idx < 0) idx += sz;
      if (idx < 0 || idx >= sz) {
        throw std::runtime_error("IndexError: string index out of range");
      }
      return PyObject(std::string(1, s[static_cast<size_t>(idx)]));
    }

    if (type == PyType::List || type == PyType::Tuple) {
      const auto& vec = std::get<std::vector<PyObject>>(value);
      long long sz = static_cast<long long>(vec.size());
      if (idx < 0) idx += sz;
      if (idx < 0 || idx >= sz) {
        throw std::runtime_error("IndexError: list index out of range");
      }
      return vec[static_cast<size_t>(idx)];
    }

    throw std::runtime_error("TypeError: '" + type_name() +
                             "' object is not subscriptable");
  }

  // Helper to get type name for error messages
  std::string type_name() const {
    switch (type) {
      case PyType::None:
        return "NoneType";
      case PyType::Int:
        return "int";
      case PyType::Float:
        return "float";
      case PyType::Bool:
        return "bool";
      case PyType::String:
        return "str";
      case PyType::List:
        return "list";
      case PyType::Set:
        return "set";
      case PyType::Dict:
        return "dict";
      case PyType::Tuple:
        return "tuple";
    }
    return "unknown";
  }

  // ==================== SET METHODS ====================

  void add(const PyObject& elem) {
    if (type != PyType::Set) {
      throw std::runtime_error("TypeError: '" + type_name() +
                               "' object has no attribute 'add'");
    }
    std::get<std::set<PyObject, PyObjectCompare>>(value).insert(elem);
  }

  void remove(const PyObject& elem) {
    if (type != PyType::Set) {
      throw std::runtime_error("TypeError: '" + type_name() +
                               "' object has no attribute 'remove'");
    }
    auto& s = std::get<std::set<PyObject, PyObjectCompare>>(value);
    auto it = s.find(elem);
    if (it == s.end()) {
      throw std::runtime_error("KeyError: " + elem.to_string());
    }
    s.erase(it);
  }

  void discard(const PyObject& elem) {
    if (type != PyType::Set) {
      throw std::runtime_error("TypeError: '" + type_name() +
                               "' object has no attribute 'discard'");
    }
    std::get<std::set<PyObject, PyObjectCompare>>(value).erase(elem);
  }

  // ==================== LIST METHODS ====================

  void append(const PyObject& elem) {
    if (type != PyType::List) {
      throw std::runtime_error("TypeError: '" + type_name() +
                               "' object has no attribute 'append'");
    }
    std::get<std::vector<PyObject>>(value).push_back(elem);
  }

  // Slice honoring optional boundaries from Python's semantics.
  PyObject slice(const PyObject& start_obj, const PyObject& end_obj,
                 bool has_start, bool has_end) const {
    if (type != PyType::List && type != PyType::Tuple &&
        type != PyType::String) {
      throw std::runtime_error("TypeError: '" + type_name() +
                               "' object is not sliceable");
    }

    const auto container_size = [&]() -> long long {
      if (type == PyType::String) {
        return static_cast<long long>(std::get<std::string>(value).size());
      }
      return static_cast<long long>(
          std::get<std::vector<PyObject>>(value).size());
    };

    const auto normalize = [&](const PyObject& idx_obj, bool provided,
                               long long fallback,
                               long long size) -> long long {
      if (!provided || idx_obj.is_none()) {
        return fallback;
      }
      long long idx = idx_obj.to_int();
      if (idx < 0) idx += size;
      if (idx < 0) idx = 0;
      if (idx > size) idx = size;
      return idx;
    };

    const long long size = container_size();
    long long start = normalize(start_obj, has_start, 0, size);
    long long end = normalize(end_obj, has_end, size, size);
    if (start > end) {
      start = end;  // Python produces empty slice when start overtakes end
    }

    if (type == PyType::String) {
      const auto& s = std::get<std::string>(value);
      return PyObject(s.substr(static_cast<size_t>(start),
                               static_cast<size_t>(end - start)));
    }

    const auto& vec = std::get<std::vector<PyObject>>(value);
    const auto slice_begin = vec.begin() + static_cast<size_t>(start);
    const auto slice_end = vec.begin() + static_cast<size_t>(end);
    std::vector<PyObject> sliced(slice_begin, slice_end);

    if (type == PyType::Tuple) {
      PyObject result;
      result.type = PyType::Tuple;
      result.value = sliced;
      return result;
    }
    return PyObject(sliced);
  }

  // Backwards-compatible helpers when both indices are positional ints.
  PyObject slice(long long start, long long end) const {
    return slice(PyObject(start), PyObject(end), true, true);
  }

  PyObject slice(long long start) const {
    return slice(PyObject(start), PyObject(), true, false);
  }

  PyObject pop(long long idx = -1) {
    if (type != PyType::List) {
      throw std::runtime_error("TypeError: '" + type_name() +
                               "' object has no attribute 'pop'");
    }
    auto& vec = std::get<std::vector<PyObject>>(value);
    long long sz = static_cast<long long>(vec.size());

    if (sz == 0) {
      throw std::runtime_error("IndexError: pop from empty list");
    }
    if (idx < 0) idx += sz;
    if (idx < 0 || idx >= sz) {
      throw std::runtime_error("IndexError: pop index out of range");
    }

    PyObject result = vec[static_cast<size_t>(idx)];
    vec.erase(vec.begin() + idx);
    return result;
  }

  const std::vector<PyObject>& get_list() const {
    if (type != PyType::List && type != PyType::Tuple) {
      throw std::runtime_error("TypeError: cannot iterate over '" +
                               type_name() + "'");
    }
    return std::get<std::vector<PyObject>>(value);
  }

  const std::set<PyObject, PyObjectCompare>& get_set() const {
    if (type != PyType::Set) {
      throw std::runtime_error("TypeError: cannot iterate over '" +
                               type_name() + "'");
    }
    return std::get<std::set<PyObject, PyObjectCompare>>(value);
  }

  // ==================== ARITHMETIC OPERATORS ====================

  PyObject operator+(const PyObject& other) const {
    if (type == PyType::String || other.type == PyType::String) {
      return PyObject(to_string() + other.to_string());
    }
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
    if (type == PyType::Float || other.type == PyType::Float) {
      return PyObject(to_float() * other.to_float());
    }
    return PyObject(to_int() * other.to_int());
  }

  PyObject operator/(const PyObject& other) const {
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

  PyObject pow(const PyObject& other) const {
    return PyObject(std::pow(to_float(), other.to_float()));
  }

  // ==================== COMPARISON OPERATORS ====================

  bool operator==(const PyObject& other) const {
    if (type != other.type) {
      if ((is_int() || is_float()) && (other.is_int() || other.is_float())) {
        return to_float() == other.to_float();
      }
      return false;
    }
    switch (type) {
      case PyType::None:
        return true;
      case PyType::Int:
        return std::get<long long>(value) == std::get<long long>(other.value);
      case PyType::Float:
        return std::get<double>(value) == std::get<double>(other.value);
      case PyType::Bool:
        return std::get<bool>(value) == std::get<bool>(other.value);
      case PyType::String:
        return std::get<std::string>(value) ==
               std::get<std::string>(other.value);
      case PyType::List:
      case PyType::Tuple:
        return std::get<std::vector<PyObject>>(value) ==
               std::get<std::vector<PyObject>>(other.value);
      case PyType::Set:
        return std::get<std::set<PyObject, PyObjectCompare>>(value) ==
               std::get<std::set<PyObject, PyObjectCompare>>(other.value);
      case PyType::Dict:
        return std::get<std::map<PyObject, PyObject, PyObjectCompare>>(value) ==
               std::get<std::map<PyObject, PyObject, PyObjectCompare>>(
                   other.value);
    }
    return false;
  }

  bool operator!=(const PyObject& other) const { return !(*this == other); }

  bool operator<(const PyObject& other) const {
    if ((is_int() || is_float()) && (other.is_int() || other.is_float())) {
      return to_float() < other.to_float();
    }
    if (type == PyType::String && other.type == PyType::String) {
      return std::get<std::string>(value) < std::get<std::string>(other.value);
    }
    throw std::runtime_error("Cannot compare these types");
  }

  bool operator>(const PyObject& other) const { return other < *this; }
  bool operator<=(const PyObject& other) const { return !(other < *this); }
  bool operator>=(const PyObject& other) const { return !(*this < other); }

  // ==================== LOGICAL OPERATORS ====================

  bool operator&&(const PyObject& other) const {
    return to_bool() && other.to_bool();
  }
  bool operator||(const PyObject& other) const {
    return to_bool() || other.to_bool();
  }
  bool operator!() const { return !to_bool(); }

  // ==================== UNARY OPERATORS ====================

  PyObject operator-() const {
    if (type == PyType::Float) {
      return PyObject(-std::get<double>(value));
    }
    return PyObject(-to_int());
  }

  PyObject operator+() const { return *this; }

  // Output operator
  friend std::ostream& operator<<(std::ostream& os, const PyObject& obj) {
    os << obj.to_string();
    return os;
  }
};

// Implementation of comparator
inline bool PyObjectCompare::operator()(const PyObject& a,
                                        const PyObject& b) const {
  if (a.get_type() != b.get_type()) {
    return static_cast<int>(a.get_type()) < static_cast<int>(b.get_type());
  }
  try {
    return a < b;
  } catch (...) {
    return a.to_string() < b.to_string();
  }
}

// ==================== GLOBAL HELPER FUNCTIONS ====================

inline PyObject floor_div(const PyObject& a, const PyObject& b) {
  return a.floor_div(b);
}
inline PyObject py_pow(const PyObject& a, const PyObject& b) {
  return a.pow(b);
}
inline size_t len(const PyObject& obj) { return obj.size(); }

// Python-faithful and/or operators (return operands, not bool)
inline PyObject py_and(const PyObject& left, const PyObject& right) {
  if (!left.to_bool()) return left;
  return right;
}

inline PyObject py_or(const PyObject& left, const PyObject& right) {
  if (left.to_bool()) return left;
  return right;
}

#endif  // PYOBJECT_H
