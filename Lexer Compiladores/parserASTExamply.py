"""
Example usage of the new AST Node system

This demonstrates:
1. How to parse code and get an AST object
2. How to use printAST() to display the tree
3. How to convert between node objects and tuples
4. How to export to JSON
"""

from ParserAST import Parser
from utils import Error
import json


def example_basic_usage():
    """Basic example: parse code and print AST"""
    print("="*60)
    print("EXAMPLE 1: Basic Usage")
    print("="*60)
    
    code = """
a = 2
a += 3
ok = (a > 1) and not (a == 0)
"""
    
    errors = []
    parser = Parser(errors, debug=False)
    parser.lexer.data = code
    
    result = parser.parser.parse(code, lexer=parser.lexer.lex)
    
    if result:
        print("\n--- Formatted AST (using printAST) ---")
        print(result.printAST())
        
        print("\n--- Tuple format (backward compatible) ---")
        print(json.dumps(result.to_tuple(), indent=2))
        
        print("\n--- Dictionary format (for JSON) ---")
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print("Parsing failed!")
        for error in errors:
            print(f"  Error: {error}")


def example_accessing_nodes():
    """Example: access specific parts of the AST"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Accessing AST Node Properties")
    print("="*60)
    
    code = """
def greet(name, greeting="Hello"):
    print(greeting, name)
    return True
"""
    
    errors = []
    parser = Parser(errors, debug=False)
    parser.lexer.data = code
    
    result = parser.parser.parse(code, lexer=parser.lexer.lex)
    
    if result:
        # Access the program's statements
        func_def = result.statements[0]
        
        print(f"Function name: {func_def.func_name}")
        print(f"Number of parameters: {len(func_def.params)}")
        
        for i, param in enumerate(func_def.params):
            if isinstance(param, tuple):
                param_name, default_val = param
                pretty = default_val.printAST(0) if hasattr(default_val, "printAST") else repr(default_val)
                print(f"  Param {i+1}: {param_name} = {pretty}")

            else:
                print(f"  Param {i+1}: {param}")
        
        print(f"\nFunction body has {len(func_def.suite)} statements:")
        for i, stmt in enumerate(func_def.suite):
            print(f"  Statement {i+1}: {type(stmt).__name__}")


def example_walking_ast():
    """Example: walk through the AST recursively"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Walking the AST")
    print("="*60)
    
    code = """
x = 5
if x > 0:
    y = x * 2
    print(y)
"""
    
    errors = []
    parser = Parser(errors, debug=False)
    parser.lexer.data = code
    
    result = parser.parser.parse(code, lexer=parser.lexer.lex)
    
    def count_nodes(node, node_type):
        """Count how many nodes of a specific type exist in the tree"""
        count = 0
        if isinstance(node, node_type):
            count = 1
        
        # Walk all attributes
        for attr_name in dir(node):
            if attr_name.startswith('_'):
                continue
            attr = getattr(node, attr_name, None)
            
            if isinstance(attr, list):
                for item in attr:
                    if hasattr(item, '__class__'):
                        count += count_nodes(item, node_type)
            elif hasattr(attr, '__class__') and hasattr(attr, 'printAST'):
                count += count_nodes(attr, node_type)
        
        return count
    
    if result:
        from ast_nodes import (AssignmentNode, IfNode, BinOpNode, 
                               IdentifierNode, LiteralNode, CallNode)
        
        print(f"Assignment nodes: {count_nodes(result, AssignmentNode)}")
        print(f"If nodes: {count_nodes(result, IfNode)}")
        print(f"Binary operation nodes: {count_nodes(result, BinOpNode)}")
        print(f"Identifier nodes: {count_nodes(result, IdentifierNode)}")
        print(f"Literal nodes: {count_nodes(result, LiteralNode)}")
        print(f"Call nodes: {count_nodes(result, CallNode)}")


def example_class_definition():
    """Example: parse a class definition"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Class Definition")
    print("="*60)
    
    code = """
class Animal:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        print(self.name, "makes a sound")
"""
    
    errors = []
    parser = Parser(errors, debug=False)
    parser.lexer.data = code
    
    result = parser.parser.parse(code, lexer=parser.lexer.lex)
    
    if result:
        class_def = result.statements[0]
        
        print(f"Class name: {class_def.class_name}")
        print(f"Parent class: {class_def.parent}")
        print(f"Number of methods: {len(class_def.body)}")
        
        print("\n--- Full AST ---")
        print(result.printAST())


def example_complex_expression():
    """Example: parse complex expressions"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Complex Expressions")
    print("="*60)
    
    code = """
result = (a + b) * c ** 2 - d / (e + 1)
chained = 0 < x < 10 <= y
logic = (flag1 or flag2) and not flag3
"""
    
    errors = []
    parser = Parser(errors, debug=False)
    parser.lexer.data = code
    
    result = parser.parser.parse(code, lexer=parser.lexer.lex)
    
    if result:
        print("--- Full AST ---")
        print(result.printAST())
        
        print("\n--- Just the expression assignments ---")
        for i, stmt in enumerate(result.statements):
            if hasattr(stmt, 'target') and hasattr(stmt, 'value'):
                target_name = stmt.target.name if hasattr(stmt.target, 'name') else str(stmt.target)
                print(f"\n{i+1}. {target_name} =")
                print(stmt.value.printAST(1))


def example_control_flow():
    """Example: parse control flow structures"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Control Flow")
    print("="*60)
    
    code = """
for i in range(10):
    if i % 2 == 0:
        print(i)
    elif i > 5:
        break
    else:
        continue

while x > 0:
    x -= 1
    try:
        result = 100 / x
    except ZeroDivisionError:
        print("Cannot divide by zero")
    except:
        print("Unknown error")
"""
    
    errors = []
    parser = Parser(errors, debug=False)
    parser.lexer.data = code
    
    result = parser.parser.parse(code, lexer=parser.lexer.lex)
    
    if result:
        print("--- Full AST ---")
        print(result.printAST())


def example_converting_formats():
    """Example: convert between different formats"""
    print("\n" + "="*60)
    print("EXAMPLE 7: Converting Between Formats")
    print("="*60)
    
    code = "x = [1, 2, 3]\ny = {'a': 1, 'b': 2}"
    
    errors = []
    parser = Parser(errors, debug=False)
    parser.lexer.data = code
    
    result = parser.parser.parse(code, lexer=parser.lexer.lex)
    
    if result:
        # Convert to tuple format
        tuple_format = result.to_tuple()
        print("Tuple format (first 200 chars):")
        print(str(tuple_format)[:200] + "...")
        
        # Convert to dict format
        dict_format = result.to_dict()
        print("\nDict format (JSON, first 500 chars):")
        json_str = json.dumps(dict_format, indent=2)
        print(json_str[:500] + "...")
        
        # Can also convert back from tuple to node
        from ast_nodes import node_from_tuple
        reconstructed = node_from_tuple(tuple_format)
        
        print("\nReconstructed from tuple:")
        print(reconstructed.printAST())


if __name__ == "__main__":
    example_basic_usage()
    example_accessing_nodes()
    example_walking_ast()
    example_class_definition()
    example_complex_expression()
    example_control_flow()
    example_converting_formats()
    
    print("\n" + "="*60)
    print("ALL EXAMPLES COMPLETED")
    print("="*60)