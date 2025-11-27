""" 
    Emmanuel
    TODO: Arreglar problemas de compilación y ejecución

    Milton 
    TODO: Cosas que el profe dijo que había que considerar

    Valentino 
    TODO: std::any o lo que sea necesario para manejar tipos dinámicos en C++
"""

import json
import subprocess
from ParserAST import Parser
from utils import Error
from ast_nodes import *

def build_and_run(file_path, mode=1):
    """
        mode=1: Solo transpilar
        mode=2: Transpilar y compilar
        mode=3: Transpilar, compilar y ejecutar
        compiler: "g++" o "clang++"
    """

    if mode > 1:
        compiler_choice = input("Compilador (1: g++ / 2: clang++): ").strip()
        if compiler_choice == "2":
            compiler = "clang++"
        else:
            compiler = "g++"

    transpiler = Transpiler()
    try:
        cpp_code = transpiler.transpile_file(file_path)
        
        with open("output.cpp", "w", encoding="utf-8") as f:
            f.write(cpp_code)
        print("[Transpilación exitosa! Output guardado en output.cpp]")
        
        if mode >= 2:
            # Use C++17 for std::variant support
            result = subprocess.run(
                [compiler, "-std=c++17", "-x", "c++", "output.cpp", "-o", "output.exe"],
                capture_output=True,
                text=True,
                shell=True,
            )
            if result.returncode != 0:
                print(f"[ERROR] Compilación falló:\n{result.stderr}")
                return
            print("[Compilación exitosa!]")
        
        if mode >= 3:
            result = subprocess.run(["output.exe"], capture_output=True, text=True)
            print(f"[Salida del programa]\n{result.stdout}")
            if result.stderr:
                print(f"[Errores]\n{result.stderr}")
                
    except Exception as e:
        print(f"[ERROR] {e}")

class Transpiler:
    def __init__(self, options=None, symbols=None):
        self.out = []
        self.indent = 0
        self.symbols = symbols or {}

    def emit(self, s): self.out.append("    " * self.indent + s)

    def transpile_file(self, file_path: str):
        """Parse a Python file and transpile it to C++."""
        errors: list[Error] = []
        parser = Parser(errors, debug=False)

        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()

        parser.lexer.data = code
        parser.lexer.lex.lineno = 1
        ast = parser.parser.parse(code, lexer=parser.lexer.lex, debug=False)

        if errors:
            error_msgs = "\n".join(str(e) for e in errors)
            raise Exception(f"Errors during parsing:\n{error_msgs}")

        if ast is None:
            raise Exception("Failed to parse file")

        return ast.accept(self)

    def visit_SetNode(self, n):
        """Handle set literals like {'a', 'b', 'c'}"""
        if not n.elements:
            return "set<PyObject, PyObjectCompare>{}"

        # Convert all elements
        elements = [elem.accept(self) for elem in n.elements]
        elements_str = ", ".join(elements)

        return f"set<PyObject, PyObjectCompare>{{{elements_str}}}"

    def visit_AttributeAccessNode(self, n):
        """Handle attribute access like obj.attr"""
        base = n.base.accept(self)
        return f"{base}.{n.attribute}"

    def visit_ProgramNode(self, n):
        # Include PyObject header
        self.emit('#include "PyObject.hpp"')
        self.emit('#include <iostream>')
        self.emit('#include <vector>')
        self.emit('#include <map>')
        self.emit('#include <tuple>')
        self.emit("using namespace std;")
        self.emit("")

        # Primero emitir funciones
        for stmt in n.statements:
            if isinstance(stmt, FuncDefNode):
                stmt.accept(self)

        # Luego el main con el resto
        self.emit("int main() {")
        self.indent += 1
        for stmt in n.statements:
            if not isinstance(stmt, FuncDefNode):
                stmt.accept(self)
        self.emit("return 0;")
        self.indent -= 1
        self.emit("}")
        return "\n".join(self.out)

    def visit_AssignmentNode(self, n):
        target = n.target
        rhs = n.value.accept(self)

        if isinstance(target, IdentifierNode):
            var_name = target.name

            if not self._is_defined(var_name):
                # First assignment - declare as PyObject
                self.emit(f"PyObject {var_name} = {rhs};")
                self._define(var_name, "PyObject")
            else:
                # Variable already exists - just assign (no redeclaration needed!)
                self.emit(f"{var_name} = {rhs};")
        else:
            self.emit(f"{target.accept(self)} = {rhs};")

    def visit_FuncDefNode(self, n):
        # Procesar parámetros (pueden ser strings o tuplas)
        processed_params = []
        for param in n.params:
            if isinstance(param, tuple):
                param_name = param[0]  # Extraer nombre de la tupla
            else:
                param_name = param     # Ya es string
            processed_params.append(f"PyObject {param_name}")

        params_str = ", ".join(processed_params)

        self.emit(f"PyObject {n.func_name}({params_str}) {{")
        self.indent += 1
        n.suite.accept(self)
        self.indent -= 1
        self.emit("}")

    def visit_ReturnNode(self, n):
        if n.value:
            value = n.value.accept(self)
            # Wrap literals in PyObject() constructor
            if isinstance(n.value, LiteralNode):
                self.emit(f"return PyObject({value});")
            else:
                self.emit(f"return {value};")
        else:
            self.emit("return PyObject();")  # Return None

    def visit_AugAssignmentNode(self, n):
        t = n.target.accept(self)
        r = n.value.accept(self)
        op = n.op
        if op == "**=":
            self.emit(f"{t} = py_pow({t}, {r});")
        elif op == "//=":
            self.emit(f"{t} = floor_div({t}, {r});")
        else:
            # Remove the '=' from the operator
            base_op = op[:-1]
            self.emit(f"{t} = {t} {base_op} {r};")

    def visit_IdentifierNode(self, n):
        return n.name

    def visit_LiteralNode(self, n):
        # Emit C++ literals and let PyObject constructors handle conversion
        if n.kind == "int":
            return str(n.value)
        if n.kind == "float":
            return str(n.value)
        if n.kind == "bool":
            return "true" if n.value else "false"
        if n.kind in ("str", "string"):
            return json.dumps(n.value)  # C++ string literal
        raise NotImplementedError(f"Unsupported literal kind: {n.kind}")

    def visit_BinaryOpNode(self, n):
        left = n.left.accept(self)
        right = n.right.accept(self)

        # Special operators
        if n.op == "**" or n.op == "pow":
            return f"py_pow({left}, {right})"
        if n.op == "//" or n.op == "floordiv":
            return f"floor_div({left}, {right})"

        # Logical operators (and/or)
        if n.op in ("and", "or"):
            cpp_op = "&&" if n.op == "and" else "||"
            # Check if operands are already boolean expressions (comparisons)
            left_needs_convert = not self._is_comparison_expr(n.left)
            right_needs_convert = not self._is_comparison_expr(n.right)

            left_expr = f"({left}).to_bool()" if left_needs_convert else left
            right_expr = f"({right}).to_bool()" if right_needs_convert else right

            return f"({left_expr} {cpp_op} {right_expr})"

        # All other operators work directly on PyObject
        return f"({left} {n.op} {right})"

    def visit_BinOpNode(self, n):
        return self.visit_BinaryOpNode(n)

    def visit_UnaryOpNode(self, n):
        expr = n.operand.accept(self)
        if n.op == "not":
            # Use PyObject's truthiness
            return f"!({expr}).to_bool()"
        return f"({n.op}{expr})"

    def visit_GroupNode(self, n):
        expr = n.expr.accept(self)
        return f"({expr})"

    def visit_ComparisonNode(self, n):
        left = n.left.accept(self)
        right = n.right.accept(self)
        return f"({left} {n.op} {right})"

    def visit_BlockNode(self, n):
        for stmt in n.statements:
            stmt.accept(self)

    def visit_IndexAccessNode(self, n):
        base = n.base.accept(self)
        index = n.index.accept(self)
        return f"{base}[{index}]"

    def visit_CallNode(self, n):
        # Handle method calls on objects (e.g., materias.add("x"), lista.append(1))
        # Check BEFORE calling accept() on callee
        if isinstance(n.callee, AttributeAccessNode):
            base = n.callee.base.accept(self)
            method = n.callee.attribute
            args = ", ".join(arg.accept(self) for arg in n.args) if n.args else ""

            # Set methods
            if method == "add":
                self.emit(f"{base}.add({args});")
                return ""
            elif method == "remove":
                self.emit(f"{base}.remove({args});")
                return ""
            elif method == "discard":
                self.emit(f"{base}.discard({args});")
                return ""
            # List methods
            elif method == "append":
                self.emit(f"{base}.append({args});")
                return ""
            elif method == "pop":
                if args:
                    return f"{base}.pop({args})"
                else:
                    return f"{base}.pop()"
            # Generic method call
            else:
                return f"{base}.{method}({args})"

        callee = n.callee.accept(self)
        args = ", ".join(arg.accept(self) for arg in n.args) if n.args else ""

        # Handle built-in functions
        if callee == "print":
            self.emit(f"cout << {args} << endl;")
            return ""
        elif callee == "str":
            # Convert to string
            return f"({args}).to_string()"
        elif callee == "len":
            # Use PyObject's size() method
            return f"len({args})"
        elif callee == "range":
            # Handle range() for for loops
            if not args:
                raise Exception("range() requires at least 1 argument")
            # Mark this as a range call for ForNode to detect
            return f"__RANGE__{args}__"

        # Regular function call
        return f"{callee}({args})"

    def visit_ArgumentNode(self, n):
        return n.value.accept(self)

    def visit_IfNode(self, n):
        # PyObject has truthiness built-in via to_bool()
        cond_expr = n.condition.accept(self)

        # Solo aplicar .to_bool() si no ya está convertido a bool por UnaryOp o Comparison
        if self._already_bool_expr(n.condition):
            condition_check = cond_expr
        else:
            condition_check = f"({cond_expr}).to_bool()"

        self.emit(f"if ({condition_check}) {{")
        self.indent += 1
        if isinstance(n.then_body, list):
            for s in n.then_body: s.accept(self)
        else:
            n.then_body.accept(self)
        self.indent -= 1

        if n.elif_clauses:
            for elif_node in n.elif_clauses:
                cond_expr = elif_node.condition.accept(self)
                if self._already_bool_expr(elif_node.condition):
                    condition_check = cond_expr
                else:
                    condition_check = f"({cond_expr}).to_bool()"
                self.emit(f"}} else if ({condition_check}) {{")
                self.indent += 1
                if isinstance(elif_node.body, list):
                    for s in elif_node.body: s.accept(self)
                else:
                    elif_node.body.accept(self)
                self.indent -= 1

        if n.else_clause:
            self.emit("} else {")
            self.indent += 1
            if isinstance(n.else_clause.body, list):
                for s in n.else_clause.body: s.accept(self)
            else:
                n.else_clause.body.accept(self)
            self.indent -= 1

        self.emit("}")

    def visit_ForNode(self, n):
        target = n.target.accept(self)
        iterable_str = n.iterable.accept(self)

        # Detectar range()
        if iterable_str.startswith("__RANGE__"):
            # Extraer el límite
            limit = iterable_str.replace("__RANGE__", "").replace("__", "")
            # Generar for tradicional de C++ con PyObject
            # Use proper PyObject increment
            self.emit(f"for (PyObject {target} = 0; ({target}).to_int() < PyObject({limit}).to_int(); {target} = PyObject(({target}).to_int() + 1)) {{")
        else:
            # Para iterar sobre PyObject con listas, usa .get_list()
            if isinstance(n.iterable, IdentifierNode):
                # Es una variable, probablemente un PyObject con lista
                self.emit(f"for (auto {target} : ({iterable_str}).get_list()) {{")
            else:
                # Es una expresión, asume que es un vector literal
                self.emit(f"for (auto {target} : {iterable_str}) {{")

        self.indent += 1
        n.body.accept(self)
        self.indent -= 1
        self.emit("}")

    def visit_WhileNode(self, n):
        """Handle while loops"""
        cond_expr = n.condition.accept(self)

        # Solo aplicar .to_bool() si no ya está convertido a bool
        if self._already_bool_expr(n.condition):
            condition_check = cond_expr
        else:
            condition_check = f"({cond_expr}).to_bool()"

        self.emit(f"while ({condition_check}) {{")
        self.indent += 1
        n.body.accept(self)
        self.indent -= 1
        self.emit("}")

    def visit_ListNode(self, n):
        """Handle list literals like [1, 2, 3]"""
        if not n.elements:
            return "vector<PyObject>{}"

        # Convert all elements
        elements = [elem.accept(self) for elem in n.elements]
        elements_str = ", ".join(elements)

        return f"vector<PyObject>{{{elements_str}}}" 

    def visit_DictNode(self, n):
        """Handle dictionary literals like {'a': 1, 'b': 2}"""
        if not n.pairs:
            return "map<PyObject, PyObject>{}"

        # Convert key-value pairs
        pairs = []
        for key, value in n.pairs:
            key_str = key.accept(self)
            val_str = value.accept(self)
            pairs.append(f"{{{key_str}, {val_str}}}")

        pairs_str = ", ".join(pairs)
        return f"map<PyObject, PyObject>{{{pairs_str}}}"

    def visit_TupleNode(self, n):
        """Handle tuple literals like (1, 2, 3)"""
        if not n.elements:
            return "tuple<>{}"

        elements = [elem.accept(self) for elem in n.elements]
        elements_str = ", ".join(elements)

        # Use tuple with PyObject
        return f"make_tuple({elements_str})"

    def _is_defined(self, name: str) -> bool:
        return name in self.symbols

    def _define(self, name: str, type_: str):
        self.symbols[name] = type_

    def _infer_type(self, node):
        """Infer C++ type from an AST node - now everything is PyObject!"""
        # For now, almost everything is PyObject
        return "PyObject"

    def _convert_to_bool(self, node, cpp_expr):
        """
        Convert an expression to bool for use in conditions.
        With PyObject, this is simple - just call .to_bool()
        """
        return f"({cpp_expr}).to_bool()"

    def _is_comparison_expr(self, node):
        """
        Check if a node represents a comparison expression that already returns bool.
        """
        return isinstance(node, ComparisonNode) or isinstance(node, ChainedComparisonNode)

    def _already_bool_expr(self, node):
        """
        Check if an expression already returns a bool value (no need to call .to_bool()).
        """
        return isinstance(node, UnaryOpNode) and node.op == "not" or \
               isinstance(node, ComparisonNode) or \
               isinstance(node, ChainedComparisonNode) or \
               isinstance(node, BinaryOpNode) and node.op in ("and", "or")

if __name__ == "__main__":
    file_path = "transpiler_tests/set_test.py"
    mode = int(input("Modo (1=transpilar, 2=compilar, 3=ejecutar): "))
    build_and_run(file_path, mode)
