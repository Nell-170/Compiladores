"""
AST Node Classes for Python-like Language Parser
Each node represents a construct in the abstract syntax tree.
"""

from typing import List, Optional, Union, Tuple, Any
import json


class ASTNode:
    """Base class for all AST nodes"""
    
    def printAST(self, indent: int = 0) -> str:
        """Return a formatted string representation of the AST"""
        raise NotImplementedError("Subclasses must implement printAST()")
    
    def to_tuple(self) -> tuple:
        """Convert to the old tuple format for backward compatibility"""
        raise NotImplementedError("Subclasses must implement to_tuple()")
    
    def to_dict(self) -> dict:
        """Convert to dictionary format for JSON serialization"""
        raise NotImplementedError("Subclasses must implement to_dict()")
    # TODO(any): def transpile(self):


# ============================================================================
# PROGRAM & TOP-LEVEL NODES
# ============================================================================

class ProgramNode(ASTNode):
    """Root node of the AST containing all top-level statements"""
    
    def __init__(self, statements: List[ASTNode]):
        self.statements = statements if statements else []
    
    def printAST(self, indent: int = 0) -> str:
        ind = "  " * indent
        lines = [f"{ind}Program:"]
        for stmt in self.statements:
            lines.append(stmt.printAST(indent + 1))
        return "\n".join(lines)
    
    def to_tuple(self) -> tuple:
        return ("program", [s.to_tuple() for s in self.statements])
    
    def to_dict(self) -> dict:
        return {
            "type": "program",
            "statements": [s.to_dict() for s in self.statements]
        }


# ============================================================================
# LITERAL & IDENTIFIER NODES
# ============================================================================

class LiteralNode(ASTNode):
    """Represents a literal value (int, float, string, bool)"""
    
    def __init__(self, kind: str, value: Any):
        self.kind = kind  # 'int', 'float', 'string', 'bool'
        self.value = value
    
    def printAST(self, indent: int = 0) -> str:
        ind = "  " * indent
        return f"{ind}Literal({self.kind}): {repr(self.value)}"
    
    def to_tuple(self) -> tuple:
        return ("literal", self.kind, self.value)
    
    def to_dict(self) -> dict:
        return {
            "type": "literal",
            "kind": self.kind,
            "value": self.value
        }


class IdentifierNode(ASTNode):
    """Represents a variable name"""
    
    def __init__(self, name: str):
        self.name = name
    
    def printAST(self, indent: int = 0) -> str:
        ind = "  " * indent
        return f"{ind}Identifier: {self.name}"
    
    def to_tuple(self) -> tuple:
        return ("identifier", self.name)
    
    def to_dict(self) -> dict:
        return {
            "type": "identifier",
            "name": self.name
        }


class AttributeAccessNode(ASTNode):
    """Represents attribute access (obj.attr or self.x)"""
    
    def __init__(self, base: Union[ASTNode, str], attribute: str):
        self.base = base if isinstance(base, ASTNode) else IdentifierNode(base)
        self.attribute = attribute
    
    def printAST(self, indent: int = 0) -> str:
        ind = "  " * indent
        lines = [f"{ind}AttributeAccess:"]
        lines.append(self.base.printAST(indent + 1))
        lines.append(f"{ind}  .{self.attribute}")
        return "\n".join(lines)
    
    def to_tuple(self) -> tuple:
        base_tuple = self.base.to_tuple() if isinstance(self.base, ASTNode) else self.base
        return ("attribute_access", base_tuple, self.attribute)
    
    def to_dict(self) -> dict:
        return {
            "type": "attribute_access",
            "base": self.base.to_dict() if isinstance(self.base, ASTNode) else self.base,
            "attribute": self.attribute
        }


# ============================================================================
# EXPRESSION NODES
# ============================================================================

class BinaryOpNode(ASTNode):
    """Binary operation (e.g., a + b, x and y)"""
    
    def __init__(self, op: str, left: ASTNode, right: ASTNode):
        self.op = op.lower()
        self.left = left
        self.right = right
    
    def printAST(self, indent: int = 0) -> str:
        ind = "  " * indent
        lines = [f"{ind}BinaryOp: {self.op}"]
        lines.append(self.left.printAST(indent + 1))
        lines.append(self.right.printAST(indent + 1))
        return "\n".join(lines)
    
    def to_tuple(self) -> tuple:
        return ("binary_op", self.op, self.left.to_tuple(), self.right.to_tuple())
    
    def to_dict(self) -> dict:
        return {
            "type": "binary_op",
            "op": self.op,
            "left": self.left.to_dict(),
            "right": self.right.to_dict()
        }


class UnaryOpNode(ASTNode):
    """Unary operation (e.g., -x, not y)"""
    
    def __init__(self, op: str, operand: ASTNode):
        self.op = op.lower()
        self.operand = operand
    
    def printAST(self, indent: int = 0) -> str:
        ind = "  " * indent
        lines = [f"{ind}UnaryOp: {self.op}"]
        lines.append(self.operand.printAST(indent + 1))
        return "\n".join(lines)
    
    def to_tuple(self) -> tuple:
        return ("unary_op", self.op, self.operand.to_tuple())
    
    def to_dict(self) -> dict:
        return {
            "type": "unary_op",
            "op": self.op,
            "operand": self.operand.to_dict()
        }


class ComparisonNode(ASTNode):
    """Simple comparison (e.g., a < b)"""
    
    def __init__(self, op: str, left: ASTNode, right: ASTNode):
        self.op = op
        self.left = left
        self.right = right
    
    def printAST(self, indent: int = 0) -> str:
        ind = "  " * indent
        lines = [f"{ind}Comparison: {self.op}"]
        lines.append(self.left.printAST(indent + 1))
        lines.append(self.right.printAST(indent + 1))
        return "\n".join(lines)
    
    def to_tuple(self) -> tuple:
        return ("comparison", self.op, self.left.to_tuple(), self.right.to_tuple())
    
    def to_dict(self) -> dict:
        return {
            "type": "comparison",
            "op": self.op,
            "left": self.left.to_dict(),
            "right": self.right.to_dict()
        }


class ChainedComparisonNode(ASTNode):
    """Chained comparison (e.g., a < b < c)"""
    
    def __init__(self, left: ASTNode, chain: List[Tuple[str, ASTNode]]):
        self.left = left
        self.chain = chain  # List of (op, expr) tuples
    
    def printAST(self, indent: int = 0) -> str:
        ind = "  " * indent
        lines = [f"{ind}ChainedComparison:"]
        lines.append(self.left.printAST(indent + 1))
        for op, expr in self.chain:
            lines.append(f"{ind}  {op}")
            lines.append(expr.printAST(indent + 1))
        return "\n".join(lines)
    
    def to_tuple(self) -> tuple:
        chain_tuples = [(op, e.to_tuple()) for op, e in self.chain]
        return ("cmp_chain", self.left.to_tuple(), chain_tuples)
    
    def to_dict(self) -> dict:
        return {
            "type": "cmp_chain",
            "left": self.left.to_dict(),
            "chain": [{"op": op, "expr": e.to_dict()} for op, e in self.chain]
        }


class GroupNode(ASTNode):
    """Parenthesized expression (not a tuple)"""
    
    def __init__(self, expr: ASTNode):
        self.expr = expr
    
    def printAST(self, indent: int = 0) -> str:
        ind = "  " * indent
        lines = [f"{ind}Group:"]
        lines.append(self.expr.printAST(indent + 1))
        return "\n".join(lines)
    
    def to_tuple(self) -> tuple:
        return ("group", self.expr.to_tuple())
    
    def to_dict(self) -> dict:
        return {
            "type": "group",
            "expr": self.expr.to_dict()
        }


# ============================================================================
# COLLECTION NODES
# ============================================================================

class TupleNode(ASTNode):
    """Tuple literal or expression"""
    
    def __init__(self, elements: List[ASTNode]):
        self.elements = elements
    
    def printAST(self, indent: int = 0) -> str:
        ind = "  " * indent
        lines = [f"{ind}Tuple:"]
        for elem in self.elements:
            lines.append(elem.printAST(indent + 1))
        return "\n".join(lines)
    
    def to_tuple(self) -> tuple:
        return ("tuple", [e.to_tuple() for e in self.elements])
    
    def to_dict(self) -> dict:
        return {
            "type": "tuple",
            "elements": [e.to_dict() for e in self.elements]
        }


class ListNode(ASTNode):
    """List literal"""
    
    def __init__(self, elements: List[ASTNode]):
        self.elements = elements
    
    def printAST(self, indent: int = 0) -> str:
        ind = "  " * indent
        lines = [f"{ind}List:"]
        for elem in self.elements:
            lines.append(elem.printAST(indent + 1))
        return "\n".join(lines)
    
    def to_tuple(self) -> tuple:
        return ("list", [e.to_tuple() for e in self.elements])
    
    def to_dict(self) -> dict:
        return {
            "type": "list",
            "elements": [e.to_dict() for e in self.elements]
        }


class DictNode(ASTNode):
    """Dictionary literal"""
    
    def __init__(self, pairs: List[Tuple[ASTNode, ASTNode]]):
        self.pairs = pairs
    
    def printAST(self, indent: int = 0) -> str:
        ind = "  " * indent
        lines = [f"{ind}Dict:"]
        for key, value in self.pairs:
            lines.append(f"{ind}  Key:")
            lines.append(key.printAST(indent + 2))
            lines.append(f"{ind}  Value:")
            lines.append(value.printAST(indent + 2))
        return "\n".join(lines)
    
    def to_tuple(self) -> tuple:
        return ("dict", [(k.to_tuple(), v.to_tuple()) for k, v in self.pairs])
    
    def to_dict(self) -> dict:
        return {
            "type": "dict",
            "pairs": [{"key": k.to_dict(), "value": v.to_dict()} for k, v in self.pairs]
        }


# ============================================================================
# CALL & ARGUMENT NODES
# ============================================================================

class CallNode(ASTNode):
    """Function/method call"""
    
    def __init__(self, callee: ASTNode, args: List['ArgumentNode']):
        self.callee = callee
        self.args = args if args else []
    
    def printAST(self, indent: int = 0) -> str:
        ind = "  " * indent
        lines = [f"{ind}Call:"]
        lines.append(self.callee.printAST(indent + 1))
        if self.args:
            lines.append(f"{ind}  Args:")
            for arg in self.args:
                lines.append(arg.printAST(indent + 2))
        return "\n".join(lines)
    
    def to_tuple(self) -> tuple:
        return ("call", self.callee.to_tuple(), [a.to_tuple() for a in self.args])
    
    def to_dict(self) -> dict:
        return {
            "type": "call",
            "callee": self.callee.to_dict(),
            "args": [a.to_dict() for a in self.args]
        }


class ArgumentNode(ASTNode):
    """Function argument (positional or keyword)"""
    
    def __init__(self, value: ASTNode, keyword: Optional[ASTNode] = None):
        self.value = value
        self.keyword = keyword  # None for positional, ASTNode for keyword
    
    def printAST(self, indent: int = 0) -> str:
        ind = "  " * indent
        if self.keyword:
            lines = [f"{ind}KeywordArg:"]
            lines.append(self.keyword.printAST(indent + 1))
            lines.append(self.value.printAST(indent + 1))
            return "\n".join(lines)
        else:
            lines = [f"{ind}PositionalArg:"]
            lines.append(self.value.printAST(indent + 1))
            return "\n".join(lines)
    
    def to_tuple(self) -> tuple:
        if self.keyword:
            return ("keyword_arg", self.keyword.to_tuple(), self.value.to_tuple())
        else:
            return ("positional_arg", self.value.to_tuple())
    
    def to_dict(self) -> dict:
        if self.keyword:
            return {
                "type": "keyword_arg",
                "keyword": self.keyword.to_dict(),
                "value": self.value.to_dict()
            }
        else:
            return {
                "type": "positional_arg",
                "value": self.value.to_dict()
            }


# ============================================================================
# STATEMENT NODES
# ============================================================================

class AssignmentNode(ASTNode):
    """Assignment statement (x = 5 or a, b = 1, 2)"""
    
    def __init__(self, target: Union[ASTNode, str], value: ASTNode):
        self.target = target if isinstance(target, ASTNode) else IdentifierNode(target)
        self.value = value
    
    def printAST(self, indent: int = 0) -> str:
        ind = "  " * indent
        lines = [f"{ind}Assignment:"]
        lines.append(f"{ind}  Target:")
        lines.append(self.target.printAST(indent + 2))
        lines.append(f"{ind}  Value:")
        lines.append(self.value.printAST(indent + 2))
        return "\n".join(lines)
    
    def to_tuple(self) -> tuple:
        target_tuple = self.target.to_tuple() if isinstance(self.target, ASTNode) else self.target
        return ("assignment", target_tuple, self.value.to_tuple())
    
    def to_dict(self) -> dict:
        return {
            "type": "assignment",
            "target": self.target.to_dict() if isinstance(self.target, ASTNode) else self.target,
            "value": self.value.to_dict()
        }


class AugAssignmentNode(ASTNode):
    """Augmented assignment (x += 5)"""
    
    def __init__(self, op: str, target: Union[ASTNode, str], value: ASTNode):
        self.op = op
        self.target = target if isinstance(target, ASTNode) else IdentifierNode(target)
        self.value = value
    
    def printAST(self, indent: int = 0) -> str:
        ind = "  " * indent
        lines = [f"{ind}AugAssignment: {self.op}"]
        lines.append(f"{ind}  Target:")
        lines.append(self.target.printAST(indent + 2))
        lines.append(f"{ind}  Value:")
        lines.append(self.value.printAST(indent + 2))
        return "\n".join(lines)
    
    def to_tuple(self) -> tuple:
        target_tuple = self.target.to_tuple() if isinstance(self.target, ASTNode) else self.target
        return ("aug_assignment", self.op, target_tuple, self.value.to_tuple())
    
    def to_dict(self) -> dict:
        return {
            "type": "aug_assignment",
            "op": self.op,
            "target": self.target.to_dict() if isinstance(self.target, ASTNode) else self.target,
            "value": self.value.to_dict()
        }


class ReturnNode(ASTNode):
    """Return statement"""
    
    def __init__(self, value: Optional[ASTNode] = None):
        self.value = value
    
    def printAST(self, indent: int = 0) -> str:
        ind = "  " * indent
        if self.value:
            lines = [f"{ind}Return:"]
            lines.append(self.value.printAST(indent + 1))
            return "\n".join(lines)
        else:
            return f"{ind}Return"
    
    def to_tuple(self) -> tuple:
        return ("return", self.value.to_tuple() if self.value else None)
    
    def to_dict(self) -> dict:
        return {
            "type": "return",
            "value": self.value.to_dict() if self.value else None
        }


class PrintNode(ASTNode):
    """Print statement"""
    
    def __init__(self, args: List[ASTNode]):
        self.args = args if args else []
    
    def printAST(self, indent: int = 0) -> str:
        ind = "  " * indent
        lines = [f"{ind}Print:"]
        for arg in self.args:
            lines.append(arg.printAST(indent + 1))
        return "\n".join(lines)
    
    def to_tuple(self) -> tuple:
        return ("print", [a.to_tuple() for a in self.args])
    
    def to_dict(self) -> dict:
        return {
            "type": "print",
            "args": [a.to_dict() for a in self.args]
        }


class PassNode(ASTNode):
    """Pass statement"""
    
    def printAST(self, indent: int = 0) -> str:
        return f"{'  ' * indent}Pass"
    
    def to_tuple(self) -> tuple:
        return ("pass",)
    
    def to_dict(self) -> dict:
        return {"type": "pass"}


class BreakNode(ASTNode):
    """Break statement"""
    
    def printAST(self, indent: int = 0) -> str:
        return f"{'  ' * indent}Break"
    
    def to_tuple(self) -> tuple:
        return ("break",)
    
    def to_dict(self) -> dict:
        return {"type": "break"}


class ContinueNode(ASTNode):
    """Continue statement"""
    
    def printAST(self, indent: int = 0) -> str:
        return f"{'  ' * indent}Continue"
    
    def to_tuple(self) -> tuple:
        return ("continue",)
    
    def to_dict(self) -> dict:
        return {"type": "continue"}


# ============================================================================
# CONTROL FLOW NODES
# ============================================================================

class IfNode(ASTNode):
    """If statement with optional elif and else clauses"""
    
    def __init__(self, condition: ASTNode, then_body: List[ASTNode], 
                 elif_clauses: List['ElifNode'], else_clause: Optional['ElseNode']):
        self.condition = condition
        self.then_body = then_body
        self.elif_clauses = elif_clauses if elif_clauses else []
        self.else_clause = else_clause
    
    def printAST(self, indent: int = 0) -> str:
        ind = "  " * indent
        lines = [f"{ind}If:"]
        lines.append(f"{ind}  Condition:")
        lines.append(self.condition.printAST(indent + 2))
        lines.append(f"{ind}  Then:")
        for stmt in self.then_body:
            lines.append(stmt.printAST(indent + 2))
        
        for elif_clause in self.elif_clauses:
            lines.append(elif_clause.printAST(indent + 1))
        
        if self.else_clause:
            lines.append(self.else_clause.printAST(indent + 1))
        
        return "\n".join(lines)
    
    def to_tuple(self) -> tuple:
        return ("if_stmt", 
                self.condition.to_tuple(), 
                [s.to_tuple() for s in self.then_body],
                [e.to_tuple() for e in self.elif_clauses],
                self.else_clause.to_tuple() if self.else_clause else None)
    
    def to_dict(self) -> dict:
        return {
            "type": "if_stmt",
            "condition": self.condition.to_dict(),
            "then_body": [s.to_dict() for s in self.then_body],
            "elif_clauses": [e.to_dict() for e in self.elif_clauses],
            "else_clause": self.else_clause.to_dict() if self.else_clause else None
        }


class ElifNode(ASTNode):
    """Elif clause"""
    
    def __init__(self, condition: ASTNode, body: List[ASTNode]):
        self.condition = condition
        self.body = body
    
    def printAST(self, indent: int = 0) -> str:
        ind = "  " * indent
        lines = [f"{ind}Elif:"]
        lines.append(f"{ind}  Condition:")
        lines.append(self.condition.printAST(indent + 2))
        lines.append(f"{ind}  Body:")
        for stmt in self.body:
            lines.append(stmt.printAST(indent + 2))
        return "\n".join(lines)
    
    def to_tuple(self) -> tuple:
        return ("elif", self.condition.to_tuple(), [s.to_tuple() for s in self.body])
    
    def to_dict(self) -> dict:
        return {
            "type": "elif",
            "condition": self.condition.to_dict(),
            "body": [s.to_dict() for s in self.body]
        }


class ElseNode(ASTNode):
    """Else clause"""
    
    def __init__(self, body: List[ASTNode]):
        self.body = body
    
    def printAST(self, indent: int = 0) -> str:
        ind = "  " * indent
        lines = [f"{ind}Else:"]
        for stmt in self.body:
            lines.append(stmt.printAST(indent + 1))
        return "\n".join(lines)
    
    def to_tuple(self) -> tuple:
        return ("else", [s.to_tuple() for s in self.body])
    
    def to_dict(self) -> dict:
        return {
            "type": "else",
            "body": [s.to_dict() for s in self.body]
        }


class WhileNode(ASTNode):
    """While loop"""
    
    def __init__(self, condition: ASTNode, body: List[ASTNode]):
        self.condition = condition
        self.body = body
    
    def printAST(self, indent: int = 0) -> str:
        ind = "  " * indent
        lines = [f"{ind}While:"]
        lines.append(f"{ind}  Condition:")
        lines.append(self.condition.printAST(indent + 2))
        lines.append(f"{ind}  Body:")
        for stmt in self.body:
            lines.append(stmt.printAST(indent + 2))
        return "\n".join(lines)
    
    def to_tuple(self) -> tuple:
        return ("while", self.condition.to_tuple(), [s.to_tuple() for s in self.body])
    
    def to_dict(self) -> dict:
        return {
            "type": "while",
            "condition": self.condition.to_dict(),
            "body": [s.to_dict() for s in self.body]
        }


class ForNode(ASTNode):
    """For loop"""
    
    def __init__(self, target: ASTNode, iterable: ASTNode, body: List[ASTNode]):
        self.target = target
        self.iterable = iterable
        self.body = body
    
    def printAST(self, indent: int = 0) -> str:
        ind = "  " * indent
        lines = [f"{ind}For:"]
        lines.append(f"{ind}  Target:")
        lines.append(self.target.printAST(indent + 2))
        lines.append(f"{ind}  Iterable:")
        lines.append(self.iterable.printAST(indent + 2))
        lines.append(f"{ind}  Body:")
        for stmt in self.body:
            lines.append(stmt.printAST(indent + 2))
        return "\n".join(lines)
    
    def to_tuple(self) -> tuple:
        return ("for", self.target.to_tuple(), self.iterable.to_tuple(), 
                [s.to_tuple() for s in self.body])
    
    def to_dict(self) -> dict:
        return {
            "type": "for",
            "target": self.target.to_dict(),
            "iterable": self.iterable.to_dict(),
            "body": [s.to_dict() for s in self.body]
        }


class TryNode(ASTNode):
    """Try-except block"""
    
    def __init__(self, try_body: List[ASTNode], except_clauses: List['ExceptNode']):
        self.try_body = try_body
        self.except_clauses = except_clauses if except_clauses else []
    
    def printAST(self, indent: int = 0) -> str:
        ind = "  " * indent
        lines = [f"{ind}Try:"]
        for stmt in self.try_body:
            lines.append(stmt.printAST(indent + 1))
        for exc in self.except_clauses:
            lines.append(exc.printAST(indent + 1))
        return "\n".join(lines)
    
    def to_tuple(self) -> tuple:
        return ("try_stmt", [s.to_tuple() for s in self.try_body],
                [e.to_tuple() for e in self.except_clauses])
    
    def to_dict(self) -> dict:
        return {
            "type": "try_stmt",
            "try_body": [s.to_dict() for s in self.try_body],
            "except_clauses": [e.to_dict() for e in self.except_clauses]
        }


class ExceptNode(ASTNode):
    """Except clause"""
    
    def __init__(self, exception_type: Optional[str], body: List[ASTNode]):
        self.exception_type = exception_type
        self.body = body
    
    def printAST(self, indent: int = 0) -> str:
        ind = "  " * indent
        exc_type = self.exception_type if self.exception_type else "all"
        lines = [f"{ind}Except ({exc_type}):"]
        for stmt in self.body:
            lines.append(stmt.printAST(indent + 1))
        return "\n".join(lines)
    
    def to_tuple(self) -> tuple:
        return ("except", self.exception_type, [s.to_tuple() for s in self.body])
    
    def to_dict(self) -> dict:
        return {
            "type": "except",
            "exception_type": self.exception_type,
            "body": [s.to_dict() for s in self.body]
        }


# ============================================================================
# DEFINITION NODES
# ============================================================================

class FuncDefNode(ASTNode):
    """Function definition"""
    
    def __init__(self, func_name: str, params: List[Union[str, Tuple[str, ASTNode]]], 
                 suite: List[ASTNode]):
        self.func_name = func_name
        self.params = params if params else []
        self.suite = suite if suite else []
    
    def printAST(self, indent: int = 0) -> str:
        ind = "  " * indent
        lines = [f"{ind}FuncDef: {self.func_name}"]
        
        if self.params:
            lines.append(f"{ind}  Params:")
            for param in self.params:
                if isinstance(param, tuple):
                    param_name, default = param
                    lines.append(f"{ind}    {param_name} = {default.printAST(0)}")
                else:
                    lines.append(f"{ind}    {param}")
        
        lines.append(f"{ind}  Body:")
        for stmt in self.suite:
            lines.append(stmt.printAST(indent + 2))
        
        return "\n".join(lines)
    
    def to_tuple(self) -> tuple:
        params_tuples = []
        for p in self.params:
            if isinstance(p, tuple):
                params_tuples.append((p[0], p[1].to_tuple()))
            else:
                params_tuples.append(p)
        
        return ("func_def", self.func_name, params_tuples, 
                [s.to_tuple() for s in self.suite])
    
    def to_dict(self) -> dict:
        params_dicts = []
        for p in self.params:
            if isinstance(p, tuple):
                params_dicts.append({"name": p[0], "default": p[1].to_dict()})
            else:
                params_dicts.append({"name": p})
        
        return {
            "type": "func_def",
            "func_name": self.func_name,
            "params": params_dicts,
            "suite": [s.to_dict() for s in self.suite]
        }


class ClassDefNode(ASTNode):
    """Class definition"""
    
    def __init__(self, class_name: str, parent: Optional[List], body: List[ASTNode]):
        self.class_name = class_name
        self.parent = parent  # Can be None or a list of parent class names
        self.body = body if body else []
    
    def printAST(self, indent: int = 0) -> str:
        ind = "  " * indent
        parent_str = f"({self.parent})" if self.parent else ""
        lines = [f"{ind}ClassDef: {self.class_name}{parent_str}"]
        
        lines.append(f"{ind}  Body:")
        for stmt in self.body:
            lines.append(stmt.printAST(indent + 2))
        
        return "\n".join(lines)
    
    def to_tuple(self) -> tuple:
        return ("class_def", self.class_name, self.parent, 
                [s.to_tuple() for s in self.body])
    
    def to_dict(self) -> dict:
        return {
            "type": "class_def",
            "class_name": self.class_name,
            "parent": self.parent,
            "body": [s.to_dict() for s in self.body]
        }


# ============================================================================
# TARGET LIST NODE (for unpacking)
# ============================================================================

class TargetListNode(ASTNode):
    """Target list for tuple unpacking (a, b, c)"""
    
    def __init__(self, targets: List[Union[ASTNode, str]]):
        self.targets = [t if isinstance(t, ASTNode) else IdentifierNode(t) 
                       for t in targets]
    
    def printAST(self, indent: int = 0) -> str:
        ind = "  " * indent
        lines = [f"{ind}TargetList:"]
        for target in self.targets:
            lines.append(target.printAST(indent + 1))
        return "\n".join(lines)
    
    def to_tuple(self) -> tuple:
        return ("target_list", [t.to_tuple() if isinstance(t, ASTNode) else t 
                               for t in self.targets])
    
    def to_dict(self) -> dict:
        return {
            "type": "target_list",
            "targets": [t.to_dict() if isinstance(t, ASTNode) else t 
                       for t in self.targets]
        }


# ============================================================================
# BINOP NODE (for arithmetic operations)
# ============================================================================

class BinOpNode(ASTNode):
    """Binary operation for arithmetic (+, -, *, /, //, %, **)"""
    
    def __init__(self, op: str, left: ASTNode, right: ASTNode):
        self.op = op
        self.left = left
        self.right = right
    
    def printAST(self, indent: int = 0) -> str:
        ind = "  " * indent
        lines = [f"{ind}BinOp: {self.op}"]
        lines.append(self.left.printAST(indent + 1))
        lines.append(self.right.printAST(indent + 1))
        return "\n".join(lines)
    
    def to_tuple(self) -> tuple:
        return ("binop", self.op, self.left.to_tuple(), self.right.to_tuple())
    
    def to_dict(self) -> dict:
        return {
            "type": "binop",
            "op": self.op,
            "left": self.left.to_dict(),
            "right": self.right.to_dict()
        }


class UnaryOpArithmeticNode(ASTNode):
    """Unary operation for arithmetic (+x, -x)"""
    
    def __init__(self, op: str, operand: ASTNode):
        self.op = op
        self.operand = operand
    
    def printAST(self, indent: int = 0) -> str:
        ind = "  " * indent
        lines = [f"{ind}UnaryOp: {self.op}"]
        lines.append(self.operand.printAST(indent + 1))
        return "\n".join(lines)
    
    def to_tuple(self) -> tuple:
        return ("unaryop", self.op, self.operand.to_tuple())
    
    def to_dict(self) -> dict:
        return {
            "type": "unaryop",
            "op": self.op,
            "operand": self.operand.to_dict()
        }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def node_from_tuple(tup) -> ASTNode:
    """Convert old tuple format back to node objects (for backward compatibility)"""
    if not isinstance(tup, tuple) or len(tup) == 0:
        return None
    
    node_type = tup[0]
    
    if node_type == "program":
        return ProgramNode([node_from_tuple(s) for s in tup[1]])
    
    elif node_type == "literal":
        return LiteralNode(tup[1], tup[2])
    
    elif node_type == "identifier":
        return IdentifierNode(tup[1])
    
    elif node_type == "attribute_access":
        base = node_from_tuple(tup[1]) if isinstance(tup[1], tuple) else tup[1]
        return AttributeAccessNode(base, tup[2])
    
    elif node_type == "binary_op":
        return BinaryOpNode(tup[1], node_from_tuple(tup[2]), node_from_tuple(tup[3]))
    
    elif node_type == "unary_op":
        return UnaryOpNode(tup[1], node_from_tuple(tup[2]))
    
    elif node_type == "comparison":
        return ComparisonNode(tup[1], node_from_tuple(tup[2]), node_from_tuple(tup[3]))
    
    elif node_type == "cmp_chain":
        chain = [(op, node_from_tuple(expr)) for op, expr in tup[2]]
        return ChainedComparisonNode(node_from_tuple(tup[1]), chain)
    
    elif node_type == "group":
        return GroupNode(node_from_tuple(tup[1]))
    
    elif node_type == "tuple":
        return TupleNode([node_from_tuple(e) for e in tup[1]])
    
    elif node_type == "list":
        return ListNode([node_from_tuple(e) for e in tup[1]])
    
    elif node_type == "dict":
        pairs = [(node_from_tuple(k), node_from_tuple(v)) for k, v in tup[1]]
        return DictNode(pairs)
    
    elif node_type == "call":
        return CallNode(node_from_tuple(tup[1]), [node_from_tuple(a) for a in tup[2]])
    
    elif node_type == "positional_arg":
        return ArgumentNode(node_from_tuple(tup[1]))
    
    elif node_type == "keyword_arg":
        return ArgumentNode(node_from_tuple(tup[2]), node_from_tuple(tup[1]))
    
    elif node_type == "assignment":
        target = node_from_tuple(tup[1]) if isinstance(tup[1], tuple) else tup[1]
        return AssignmentNode(target, node_from_tuple(tup[2]))
    
    elif node_type == "aug_assignment":
        target = node_from_tuple(tup[2]) if isinstance(tup[2], tuple) else tup[2]
        return AugAssignmentNode(tup[1], target, node_from_tuple(tup[3]))
    
    elif node_type == "return":
        return ReturnNode(node_from_tuple(tup[1]) if tup[1] else None)
    
    elif node_type == "print":
        return PrintNode([node_from_tuple(a) for a in tup[1]])
    
    elif node_type == "pass":
        return PassNode()
    
    elif node_type == "break":
        return BreakNode()
    
    elif node_type == "continue":
        return ContinueNode()
    
    elif node_type == "if_stmt":
        elif_clauses = [node_from_tuple(e) for e in tup[3]]
        else_clause = node_from_tuple(tup[4]) if tup[4] else None
        return IfNode(node_from_tuple(tup[1]), [node_from_tuple(s) for s in tup[2]],
                     elif_clauses, else_clause)
    
    elif node_type == "elif":
        return ElifNode(node_from_tuple(tup[1]), [node_from_tuple(s) for s in tup[2]])
    
    elif node_type == "else":
        return ElseNode([node_from_tuple(s) for s in tup[1]])
    
    elif node_type == "while":
        return WhileNode(node_from_tuple(tup[1]), [node_from_tuple(s) for s in tup[2]])
    
    elif node_type == "for":
        return ForNode(node_from_tuple(tup[1]), node_from_tuple(tup[2]),
                      [node_from_tuple(s) for s in tup[3]])
    
    elif node_type == "try_stmt":
        return TryNode([node_from_tuple(s) for s in tup[1]],
                      [node_from_tuple(e) for e in tup[2]])
    
    elif node_type == "except":
        return ExceptNode(tup[1], [node_from_tuple(s) for s in tup[2]])
    
    elif node_type == "func_def":
        params = []
        for p in tup[2]:
            if isinstance(p, tuple):
                params.append((p[0], node_from_tuple(p[1])))
            else:
                params.append(p)
        return FuncDefNode(tup[1], params, [node_from_tuple(s) for s in tup[3]])
    
    elif node_type == "class_def":
        return ClassDefNode(tup[1], tup[2], [node_from_tuple(s) for s in tup[3]])
    
    elif node_type == "target_list":
        targets = [node_from_tuple(t) if isinstance(t, tuple) else t for t in tup[1]]
        return TargetListNode(targets)
    
    elif node_type == "binop":
        return BinOpNode(tup[1], node_from_tuple(tup[2]), node_from_tuple(tup[3]))
    
    elif node_type == "unaryop":
        return UnaryOpArithmeticNode(tup[1], node_from_tuple(tup[2]))
    
    return None