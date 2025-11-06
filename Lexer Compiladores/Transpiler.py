import json

class Transpiler:
    def __init__(self, options=None, symbols=None):
        self.out = []
        self.indent = 0
        self.symbols = symbols or {}

    def emit(self, s): self.out.append("    " * self.indent + s)

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
        # decide on declaration vs assignment using symbol table
        # simple example, assume ints unless inferred otherwise:
        target = n.target  # IdentifierNode or more complex
        rhs = n.value.accept(self)
        if isinstance(target, IdentifierNode) and not self._is_defined(target.name):
            self.emit(f"int {target.name} = {rhs};")
            self._define(target.name, "int")
        else:
            self.emit(f"{target.accept(self)} = {rhs};")

    def visit_AugAssignmentNode(self, n):
        # careful with '**=' and '//=' differences (see helpers below)
        t = n.target.accept(self)
        r = n.value.accept(self)
        op = n.op
        if op == "**=":
            self.emit(f"{t} = (int)std::pow({t}, {r});")
        elif op == "//=":
            self.emit(f"{t} = floor_div({t}, {r});")
        else:
            self.emit(f"{t} {op} {r};")  # +=, -=, *=, /=, %=, etc.

    def visit_IdentifierNode(self, n):
        return n.name

    def visit_LiteralNode(self, n):
        if n.kind == "int":   return str(n.value)
        if n.kind == "float": return str(n.value)
        if n.kind == "bool":  return "true" if n.value else "false"
        if n.kind == "str":   return json.dumps(n.value)  # or quoted
        raise NotImplementedError(n.kind)

    def visit_BinaryOpNode(self, n):
        left = n.left.accept(self)
        right = n.right.accept(self)
        if n.op == "**":
            return f"(int)std::pow({left}, {right})"
        if n.op == "//":
            return f"floor_div({left}, {right})"
        if n.op in ("and", "or"):
            # C++ short-circuits with && and ||
            cpp = "&&" if n.op == "and" else "||"
            return f"({left} {cpp} {right})"
        # + - * / % < > <= >= == != etc.
        return f"({left} {n.op} {right})"

    def visit_UnaryOpNode(self, n):
        expr = n.operand.accept(self)
        if n.op == "not": return f"(!{expr})"
        return f"({n.op}{expr})"

    def visit_IfNode(self, n):
        cond = n.test.accept(self)
        self.emit(f"if ({cond}) {{")
        self.indent += 1
        for s in n.body: s.accept(self)
        self.indent -= 1
        if n.elifs:
            for econd, ebody in n.elifs:
                cond = econd.accept(self)
                self.emit(f"}} else if ({cond}) {{")
                self.indent += 1
                for s in ebody: s.accept(self)
                self.indent -= 1
        if n.orelse:
            self.emit("} else {")
            self.indent += 1
            for s in n.orelse: s.accept(self)
            self.indent -= 1
        self.emit("}")