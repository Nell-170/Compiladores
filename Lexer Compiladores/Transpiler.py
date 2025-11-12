""" Emmanuel
    TODO:   Generar el código C++ a partir del AST
            Generarlo y compilarlo con g++ 
            Generarlo, compilarlo y ejecutarlo, capturando la salida

            For con print (e)

    Milton 
    TODO: while a < b:
          a = 10

    Valentino 
    TODO:  b=c-2
"""

import json
from ParserAST import Parser
from utils import Error
from ast_nodes import *

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

        return ast.accept(self) # Aquí comienza el visitor

    def visit_ProgramNode(self, n):
        self.emit("#include <bits/stdc++.h>")
        self.emit("using namespace std;")
        self.emit("")
        self.emit("int main() {")
        self.indent += 1
        for stmt in n.statements:
            stmt.accept(self)
        self.emit("return 0;")
        self.indent -= 1
        self.emit("}")
        return "\n".join(self.out)

    def visit_AssignmentNode(self, n):
        target = n.target
        rhs = n.value.accept(self)
        if isinstance(target, IdentifierNode) and not self._is_defined(target.name):
            self.emit(f"int {target.name} = {rhs};")
            self._define(target.name, "int")
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
        
        self.emit(f"int {n.func_name}({params_str}) {{")  # Usar n.func_name
        self.indent += 1
        n.suite.accept(self)  # Usar n.suite en lugar de n.body
        self.indent -= 1
        self.emit("}")

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
        if n.kind == "int":   return str(n.value)
        if n.kind == "float": return str(n.value)
        if n.kind == "bool":  return "true" if n.value else "false"
        if n.kind == "str":   return json.dumps(n.value)
        raise NotImplementedError(n.kind)

    def visit_BinaryOpNode(self, n):
        left = n.left.accept(self)
        right = n.right.accept(self)
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
        if callee == "print":
            self.emit(f"cout << {args} << endl;")
            return ""
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
            self.emit(f"for (int {target} = 0; {target} < {limit}; {target}++) {{")
        else:
            # Range-based for normal
            self.emit(f"for (auto {target} : {iterable_str}) {{")
        
        self.indent += 1
        n.body.accept(self)
        self.indent -= 1
        self.emit("}")

    def _is_defined(self, name: str) -> bool:
        return name in self.symbols

    def _define(self, name: str, type_: str):
        self.symbols[name] = type_

if __name__ == "__main__":
    transpiler = Transpiler()
    try:
        cpp_code = transpiler.transpile_file("transpiler_tests/simple_test.py")

        # Optionally save to file
        with open("output.cpp", "w", encoding="utf-8") as f:
            f.write(cpp_code)
        print("\n[Transpilation successful! Output saved to output.cpp]")
    except Exception as e:
        print(f"[ERROR] {e}")

 