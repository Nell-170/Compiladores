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

    def visit_ArgumentNode(self, n):
        """Handle function arguments (positional or keyword)"""
        if n.keyword:
            # Keyword argument: name=value
            key_name = (
                n.keyword.accept(self)
                if isinstance(n.keyword, ASTNode)
                else str(n.keyword)
            )
            value = n.value.accept(self)
            return f"{key_name}={value}"
        else:
            # Positional argument
            return n.value.accept(self)

    def visit_IfNode(self, n):
        """Handle if statement with elif and else"""
        condition = n.condition.accept(self)
        self.emit(f"if ({condition}) {{")
        self.indent += 1
        n.then_body.accept(self)
        self.indent -= 1

        # Handle elif clauses
        for elif_clause in n.elif_clauses:
            elif_clause.accept(self)

        # Handle else clause
        if n.else_clause:
            n.else_clause.accept(self)

        self.emit("}")

    def visit_ElifNode(self, n):
        """Handle elif clause"""
        condition = n.condition.accept(self)
        self.emit(f"}} else if ({condition}) {{")
        self.indent += 1
        n.body.accept(self)
        self.indent -= 1

    def visit_ElseNode(self, n):
        """Handle else clause"""
        self.emit("} else {")
        self.indent += 1
        n.body.accept(self)
        self.indent -= 1

    def visit_WhileNode(self, n):
        """Handle while loop"""
        condition = n.condition.accept(self)
        self.emit(f"while ({condition}) {{")
        self.indent += 1
        n.body.accept(self)
        self.indent -= 1
        self.emit("}")

    def visit_ForNode(self, n):
        """Handle for loop (transpile to range-based for or iterator)"""
        target_name = (
            n.target.accept(self) if hasattr(n.target, "accept") else str(n.target)
        )
        iterable = n.iterable.accept(self)

        # Check if iterable is a range() call
        if "RANGE__" in iterable:
            # Extract range parameters
            range_str = iterable.replace("__RANGE__", "").replace("__", "")
            self.emit(
                f"for (int {target_name} = 0; {target_name} < {range_str}; {target_name}++) {{"
            )
        else:
            # Generic for-each loop
            self.emit(f"for (auto {target_name} : {iterable}) {{")

        self.indent += 1
        n.body.accept(self)
        self.indent -= 1
        self.emit("}")

    def visit_TryNode(self, n):
        """Handle try-except block"""
        self.emit("try {")
        self.indent += 1
        n.try_body.accept(self)
        self.indent -= 1
        self.emit("}")

        for except_clause in n.except_clauses:
            except_clause.accept(self)

    def visit_ExceptNode(self, n):
        """Handle except clause"""
        if n.exception_type:
            self.emit(f"catch (const {n.exception_type}& e) {{")
        else:
            self.emit("catch (...) {")

        self.indent += 1
        n.handler_body.accept(self)
        self.indent -= 1
        self.emit("}")

    def visit_PassNode(self, n):
        """Handle pass statement"""
        self.emit("// pass")

    def visit_BreakNode(self, n):
        """Handle break statement"""
        self.emit("break;")

    def visit_ContinueNode(self, n):
        """Handle continue statement"""
        self.emit("continue;")

    def visit_PrintNode(self, n):
        """Handle print statement"""
        if not n.args:
            self.emit("cout << endl;")
            return

        # Check if any arg is a set or dict
        for arg in n.args:
            if isinstance(arg, IdentifierNode):
                var_type = self.symbols.get(arg.name, "")
                if "set<" in var_type:
                    self.emit(f"print_set({arg.accept(self)});")
                    return
                elif "map<" in var_type:
                    self.emit(f"print_map({arg.accept(self)});")
                    return

        # Normal print
        args_str = " << ".join(arg.accept(self) for arg in n.args)
        self.emit(f"cout << {args_str} << endl;")

    def visit_TupleNode(self, n):
        """Handle tuple (convert to C++ tuple or struct)"""
        elements = [elem.accept(self) for elem in n.elements]
        return f"make_tuple({', '.join(elements)})"

    def visit_ListNode(self, n):
        """Handle list literal"""
        if not n.elements:
            return "vector<int>{}"

        elements = [elem.accept(self) for elem in n.elements]
        elements_str = ", ".join(elements)
        return f"vector<string>{{{elements_str}}}"

    def visit_TargetListNode(self, n):
        """Handle target list for unpacking"""
        targets = []
        for t in n.targets:
            if isinstance(t, ASTNode):
                targets.append(t.accept(self))
            else:
                targets.append(str(t))
        return ", ".join(targets)

    def visit_ClassDefNode(self, n):
        """Handle class definition (basic support)"""
        parents = ", ".join(f"public {p}" for p in n.parent) if n.parent else ""

        self.emit(f"class {n.class_name}" + (f" : {parents}" if parents else "") + " {")
        self.emit("public:")
        self.indent += 1
        n.body.accept(self)
        self.indent -= 1
        self.emit("};")

    def visit_ProgramNode(self, n):
        self.emit("#include <iostream>")
        self.emit("#include <string>")
        self.emit("#include <vector>")
        self.emit("#include <map>")
        self.emit("#include <set>")
        self.emit("#include <tuple>")
        self.emit("using namespace std;")
        self.emit("")

        # Helper function para imprimir sets
        self.emit("template<typename T>")
        self.emit("void print_set(const set<T>& s) {")
        self.indent += 1
        self.emit('cout << "{";')
        self.emit("bool first = true;")
        self.emit("for (const auto& elem : s) {")
        self.indent += 1
        self.emit('if (!first) cout << ", ";')
        self.emit('cout << "\\"" << elem << "\\"";')  # Agregar comillas a strings
        self.emit("first = false;")
        self.indent -= 1
        self.emit("}")
        self.emit('cout << "}" << endl;')
        self.indent -= 1
        self.emit("}")
        self.emit("")

        # Helper function para imprimir maps
        self.emit("template<typename K, typename V>")
        self.emit("void print_map(const map<K, V>& m) {")
        self.indent += 1
        self.emit('cout << "{";')
        self.emit("bool first = true;")
        self.emit("for (const auto& pair : m) {")
        self.indent += 1
        self.emit('if (!first) cout << ", ";')
        self.emit('cout << "\\"" << pair.first << "\\": " << pair.second;')
        self.emit("first = false;")
        self.indent -= 1
        self.emit("}")
        self.emit('cout << "}" << endl;')
        self.indent -= 1
        self.emit("}")
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

        # Caso especial: asignación a índice (dict["key"] = value)
        if isinstance(target, IndexAccessNode):
            base = target.base.accept(self)
            index = target.index.accept(self)
            self.emit(f"{base}[{index}] = {rhs};")
            return

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

    def visit_DictNode(self, n):
        """Handle dict literals like {"name": "John", "age": 25}"""
        if not n.pairs:
            return "map<string, int>{}"

        # Convert all key-value pairs
        pairs_str = ", ".join(
            f"{{{k.accept(self)}, {v.accept(self)}}}" for k, v in n.pairs
        )

        # Para simplificar, usar map<string, int>
        # En producción necesitarías inferencia de tipos más sofisticada
        return f"map<string, int>{{{pairs_str}}}"

    def visit_SetNode(self, n):
        """Handle set literals like {"a", "b", "c"}"""
        if not n.elements:
            return "set<string>{}"

        # Convert all elements
        elements = [elem.accept(self) for elem in n.elements]
        elements_str = ", ".join(elements)

        # Para simplificar, usar set<string>
        return f"set<string>{{{elements_str}}}"

    def visit_AttributeAccessNode(self, n):
        """Handle attribute access like obj.attr"""
        base = n.base.accept(self)
        attr = n.attribute
        return f"{base}.{attr}"

    def visit_CallNode(self, n):
        callee = n.callee.accept(self)

        arg_strings = []
        value_exprs = []
        value_strings = []
        if n.args:
            for arg in n.args:
                arg_strings.append(arg.accept(self))
                expr = arg.value if isinstance(arg, ArgumentNode) else arg
                value_exprs.append(expr)
                value_strings.append(expr.accept(self))
        args = ", ".join(arg_strings)

        # Manejar métodos de set/list/dict
        if isinstance(n.callee, AttributeAccessNode):
            base = n.callee.base.accept(self)
            method = n.callee.attribute

            # Métodos de set
            if method == "add":
                arg = n.args[0].accept(self) if n.args else ""
                self.emit(f"{base}.insert({arg});")
                return ""
            elif method == "remove":
                arg = n.args[0].accept(self) if n.args else ""
                self.emit(f"{base}.erase({arg});")
                return ""

            # Métodos de list
            elif method == "append":
                arg = n.args[0].accept(self) if n.args else ""
                self.emit(f"{base}.push_back({arg});")
                return ""
            elif method == "pop":
                if n.args:
                    index = n.args[0].accept(self)
                    return f"{base}.erase({base}.begin() + {index})"
                else:
                    self.emit(f"{base}.pop_back();")
                    return ""

            # Métodos de dict
            elif method == "get":
                key = n.args[0].accept(self) if n.args else ""
                default = n.args[1].accept(self) if len(n.args) > 1 else "0"
                return f"({base}.count({key}) ? {base}[{key}] : {default})"
            elif method == "keys":
                return f"/* keys() not directly supported in C++ */"
            elif method == "values":
                return f"/* values() not directly supported in C++ */"

        args = ", ".join(arg.accept(self) for arg in n.args) if n.args else ""

        # Handle built-in functions
        if callee == "print":
            if not value_exprs:
                self.emit("cout << endl;")
                return ""
            if len(value_exprs) == 1:
                expr = value_exprs[0]
                expr_code = value_strings[0]
                if isinstance(expr, IdentifierNode):
                    var_type = self.symbols.get(expr.name, "")
                    if "set<" in var_type:
                        self.emit(f"print_set({expr_code});")
                        return ""
                    elif "map<" in var_type:
                        self.emit(f"print_map({expr_code});")
                        return ""
            self.emit(f"cout << {' << '.join(value_strings)} << endl;")
            return ""
        elif callee == "str":
            return f"to_string({args})"
        elif callee == "len":
            return f"({args}).size()"
        elif callee == "range":
            if not args:
                raise Exception("range() requires at least 1 argument")
            return f"__RANGE__{args}__"

        # Regular function call
        return f"{callee}({args})"

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
            return "vector<string>"  # Simplificado
        elif isinstance(node, SetNode):
            return "set<string>"  # Simplificado
        elif isinstance(node, DictNode):
            return "map<string, ssize_t>"  # Simplificado
        elif isinstance(node, TupleNode):
            return "tuple<int, int>"  # Simplificado
        elif isinstance(node, BinaryOpNode) or isinstance(node, BinOpNode):
            return self._infer_type(node.left)
        elif isinstance(node, GroupNode):
            return self._infer_type(node.expr)
        elif isinstance(node, CallNode):
            callee = node.callee.accept(self) if hasattr(node.callee, 'accept') else str(node.callee)
            if callee == "str":
                return "string"
            elif callee == "len":
                return "int"
            return "int"
        elif isinstance(node, IdentifierNode):
            return self.symbols.get(node.name, "int")

        # Default fallback
        return "int"

if __name__ == "__main__":
    file_path = "transpiler_tests/dict_test.py"
    mode = int(input("Modo (1=transpilar, 2=compilar, 3=ejecutar): "))
    build_and_run(file_path, mode)
