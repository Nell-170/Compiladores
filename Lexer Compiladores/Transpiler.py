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
import sys
import os
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
            result = subprocess.run(
                [compiler, "-x", "c++", "output.cpp", "-o", "output.exe", "-lstdc++"],
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

    def visit_ProgramNode(self, n):
        self.emit("#include <iostream>")
        self.emit("#include <string>")
        self.emit("#include <vector>")
        self.emit("#include <map>")
        self.emit("#include <cstddef>")
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

            # Infer type from the right-hand side
            inferred_type = self._infer_type(n.value)

            if not self._is_defined(var_name):
                # First assignment - declare with inferred type
                self.emit(f"{inferred_type} {var_name} = {rhs};")
                self._define(var_name, inferred_type)
            else:
                # Variable already exists - check if type changed
                old_type = self.symbols[var_name]
                if old_type != inferred_type:
                    # Type changed! Need to redeclare
                    self.emit(f"{inferred_type} {var_name} = {rhs};")
                    self.symbols[var_name] = inferred_type
                else:
                    # Same type, just assign
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
            processed_params.append(f"int {param_name}")

        params_str = ", ".join(processed_params)

        self.emit(f"int {n.func_name}({params_str}) {{")
        self.indent += 1
        n.suite.accept(self)
        self.indent -= 1
        self.emit("}")

    def visit_ReturnNode(self, n):
        value = n.value.accept(self)
        self.emit(f"return {value};")

    def visit_AugAssignmentNode(self, n):
        t = n.target.accept(self)
        r = n.value.accept(self)
        op = n.op
        if op == "**=":
            self.emit(f"{t} = (int)std::pow({t}, {r});")
        elif op == "//=":
            self.emit(f"{t} = floor_div({t}, {r});")
        else:
            self.emit(f"{t} {op} {r};")

    def visit_IdentifierNode(self, n):
        return n.name

    def visit_LiteralNode(self, n):
        if n.kind == "int":     return str(n.value)
        if n.kind == "float":   return str(n.value)
        if n.kind == "bool":    return "true" if n.value else "false"
        if n.kind in ("str", "string"): return json.dumps(n.value)  # Changed from "str" to "string"
        raise NotImplementedError(f"Unsupported literal kind: {n.kind}")

    def visit_BinaryOpNode(self, n):
        left = n.left.accept(self)
        right = n.right.accept(self)

        # Handle string concatenation with +
        if n.op == "+":
            left_type = self._infer_type(n.left)
            right_type = self._infer_type(n.right)
            # If either operand is a string, this is string concatenation
            if "string" in left_type or "string" in right_type:
                return f"({left} + {right})"

        if n.op == "**" or n.op == "pow":
            return f"(int)std::pow({left}, {right})"
        if n.op == "//" or n.op == "floordiv":
            return f"floor_div({left}, {right})"
        if n.op in ("and", "or"):
            cpp = "&&" if n.op == "and" else "||"
            return f"({left} {cpp} {right})"
        return f"({left} {n.op} {right})"

    def visit_BinOpNode(self, n):
        return self.visit_BinaryOpNode(n)

    def visit_UnaryOpNode(self, n):
        expr = n.operand.accept(self)
        if n.op == "not": return f"(!{expr})"
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
        callee = n.callee.accept(self)
        args = ", ".join(arg.accept(self) for arg in n.args) if n.args else ""

        # Handle built-in functions
        if callee == "print":
            self.emit(f"cout << {args} << endl;")
            return ""
        elif callee == "str":
            # Convert to string
            return f"to_string({args})"
        elif callee == "len":
            # Get length of container
            return f"({args}).size()"
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
        cond = n.condition.accept(self)
        self.emit(f"if ({cond}) {{")
        self.indent += 1
        if isinstance(n.then_body, list):
            for s in n.then_body: s.accept(self)
        else:
            n.then_body.accept(self)
        self.indent -= 1

        if n.elif_clauses:
            for elif_node in n.elif_clauses:
                cond = elif_node.condition.accept(self)
                self.emit(f"}} else if ({cond}) {{")
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
            # Generar for tradicional de C++
            self.emit(f"for (ssize_t {target} = 0; {target} < {limit}; {target}++) {{")
        else:
            # Range-based for normal
            self.emit(f"for (auto {target} : {iterable_str}) {{")

        self.indent += 1
        n.body.accept(self)
        self.indent -= 1
        self.emit("}")

    ## ! SUGERENCIAS, PERO HECHAS MUY RÁPIDAMENTE, SOLO PARA PODER PROBAR STRINGS

    def visit_WhileNode(self, n):
        """Handle while loops"""
        cond = n.condition.accept(self)
        self.emit(f"while ({cond}) {{")
        self.indent += 1
        n.body.accept(self)
        self.indent -= 1
        self.emit("}")

    def visit_ListNode(self, n):
        """Handle list literals like [1, 2, 3]"""
        if not n.elements:
            return "vector<ssize_t>{}"

        # Convert all elements
        elements = [elem.accept(self) for elem in n.elements]
        elements_str = ", ".join(elements)

        # For simplicity, use vector<int> or detect if all are same type
        # In production, you'd want better type inference
        return f"vector<ssize_t>{{{elements_str}}}" 

    def visit_DictNode(self, n):
        """Handle dictionary literals like {'a': 1, 'b': 2}"""
        if not n.pairs:
            return "map<string, ssize_t>{}"

        # Convert key-value pairs
        pairs = []
        for key, value in n.pairs:
            key_str = key.accept(self)
            val_str = value.accept(self)
            pairs.append(f"{{{key_str}, {val_str}}}")

        pairs_str = ", ".join(pairs)
        return f"map<string, ssize_t>{{{pairs_str}}}"

    def visit_TupleNode(self, n):
        """Handle tuple literals like (1, 2, 3)"""
        if not n.elements:
            return "tuple<>{}"

        elements = [elem.accept(self) for elem in n.elements]
        elements_str = ", ".join(elements)

        # Use tuple or just braced init for simplicity
        return f"make_tuple({elements_str})"

    def _is_defined(self, name: str) -> bool:
        return name in self.symbols

    def _define(self, name: str, type_: str):
        self.symbols[name] = type_

    def _infer_type(self, node):
        """Infer C++ type from an AST node"""
        if isinstance(node, LiteralNode):
            if node.kind == "int":
                return "ssize_t"
            elif node.kind == "float":
                return "double"
            elif node.kind == "string":
                return "string"
            elif node.kind == "bool":
                return "bool"
        elif isinstance(node, ListNode):
            return "vector<int>"  # Simplified - would need element type inference
        elif isinstance(node, DictNode):
            return "map<string, int>"  # Simplified
        elif isinstance(node, TupleNode):
            return "tuple<int, int>"  # Simplified
        elif isinstance(node, BinaryOpNode) or isinstance(node, BinOpNode):
            # For binary operations, try to infer from left operand
            return self._infer_type(node.left)
        elif isinstance(node, GroupNode):
            return self._infer_type(node.expr)
        elif isinstance(node, CallNode):
            callee = node.callee.accept(self) if hasattr(node.callee, 'accept') else str(node.callee)
            if callee == "str":
                return "string"
            elif callee == "len":
                return "int"
            # Default for function calls
            return "int"
        elif isinstance(node, IdentifierNode):
            # Look up in symbol table
            return self.symbols.get(node.name, "int")

        # Default fallback
        return "int"

if __name__ == "__main__":
    file_path = "transpiler_tests/teacher_test.py"
    mode = int(input("Modo (1=transpilar, 2=compilar, 3=ejecutar): "))
    build_and_run(file_path, mode)