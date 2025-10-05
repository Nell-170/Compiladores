import ply.yacc as yacc
import sys
from Lexer import Lexer
from utils import Error
import ast
import json

class Parser:
# ----- PRECEDENCIA Y ASOCIATIVIDAD -----
    precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
    ('left', 'LESS', 'GREATER', 'LESSEQ', 'GREATEREQ', 'EQ', 'NEQ'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTI', 'DIVIDE', 'FLOORDIV', 'MOD'),
    ('right', 'UMINUS', 'UPLUS'),  # Operadores unarios
    ('right', 'POW'),
    )

    def __init__(self, errors: list[Error], debug=False):
        self.errors = errors
        self.debug = debug
        self.lexer = Lexer(errors, debug)
        self.lexer.build()
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self, start="program", debug=debug)

       # --- helpers AST (solo para expresiones; no afectan otros segmentos) ---
    def _bin(self, op, left, right):
        return ("binary_op", op.lower(), left, right)

    def _un(self, op, operand):
        return ("unary_op", op.lower(), operand)

    def _lit(self, kind, value):
        return ("literal", kind, value)

    def _id(self, name):
        return ("identifier", name)


    # ----- Reglas de la gramática -----
    # Programa: lista de sentencias (puede ser función, clase o expresión simple)
    def p_program(self, p):
        """program : top_level_stmts"""
        p[0] = ("program", p[1]) # AST raíz: tipo 'program', con lista de sentencias

    # ----- SENTENCIAS DE NIVEL SUPERIOR (módulo) -----
    # Solo en el nivel superior se permiten definiciones de clases y funciones
    def p_top_level_stmts(self, p):
        """top_level_stmts : top_level_stmts top_level_stmt
                           | top_level_stmt
                           | empty"""
        if len(p) == 3:
            if p[1] is None:
                p[0] = [p[2]]
            else:
                p[0] = p[1] + [p[2]]
        elif p[1] is None:
            p[0] = []
        else:
            p[0] = [p[1]]

    def p_top_level_stmt(self, p):
        """top_level_stmt : func_def
                         | class_def
                         | simple_stmt"""
        p[0] = p[1]

    # ----- SENTENCIAS DENTRO DE FUNCIONES -----
    # Dentro de funciones NO se permiten definiciones de clases ni funciones anidadas
    def p_func_body_stmts(self, p):
        """func_body_stmts : func_body_stmts func_body_stmt
                          | func_body_stmt
                          | empty"""
        if len(p) == 3:
            if p[1] is None:
                p[0] = [p[2]]
            else:
                p[0] = p[1] + [p[2]]
        elif p[1] is None:
            p[0] = []
        else:
            p[0] = [p[1]]

    def p_func_body_stmt(self, p):
        """func_body_stmt : simple_stmt
                         | if_stmt
                         | while_stmt
                         | for_stmt"""
        p[0] = p[1]


    # ----- SENTENCIAS DENTRO DE CLASES -----
    # Dentro de clases se permiten métodos (funciones) pero NO clases anidadas
    def p_class_body_stmts(self, p):
        """class_body_stmts : class_body_stmts class_body_stmt
                           | class_body_stmt
                           | empty"""
        if len(p) == 3:
            if p[1] is None:
                p[0] = [p[2]]
            else:
                p[0] = p[1] + [p[2]]
        elif p[1] is None:
            p[0] = []
        else:
            p[0] = [p[1]]

    def p_class_body_stmt(self, p):
        """class_body_stmt : func_def
                          | simple_stmt"""
        p[0] = p[1]

     # ----- SENTENCIAS DENTRO DE BLOQUES DE CONTROL -----
    # En if/while/for se permiten todas las sentencias excepto def. de clases / funciones
    def p_block_stmts(self, p):
        """block_stmts : block_stmts block_stmt
                      | block_stmt
                      | empty"""
        if len(p) == 3:
            if p[1] is None:
                p[0] = [p[2]]
            else:
                p[0] = p[1] + [p[2]]
        elif p[1] is None:
            p[0] = []
        else:
            p[0] = [p[1]]

    def p_block_stmt(self, p):
        """block_stmt : simple_stmt
                     | if_stmt
                     | while_stmt
                     | for_stmt"""
        p[0] = p[1]

    # ----- DEFINICIÓN DE FUNCIONES -----
    def p_func_def(self, p):
        """func_def : DEF ID LPAREN params_list RPAREN COLON NEWLINE INDENT func_body_stmts DEDENT
                    | DEF ID LPAREN RPAREN COLON NEWLINE INDENT func_body_stmts DEDENT"""
        if len(p) == 11:
            p[0] = ("func_def", p[2], p[4], p[9])  # nombre, parámetros, cuerpo
        else:
            p[0] = ("func_def", p[2], [], p[8])  # nombre, sin parámetros, cuerpo

    # Lista de parámetros
    def p_params_list(self, p):
        """params_list : params_list COMMA ID
                      | ID"""
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]

    # ----- DEFINICIÓN DE CLASES -----
    def p_class_def(self, p):
        """class_def : CLASS ID COLON NEWLINE INDENT class_body_stmts DEDENT
                     | CLASS ID LPAREN ID RPAREN COLON NEWLINE INDENT class_body_stmts DEDENT"""
        if len(p) == 8:
            p[0] = ("class_def", p[2], None, p[6])  # nombre, sin herencia, cuerpo
        else:
            p[0] = ("class_def", p[2], p[4], p[9])  # nombre, clase padre, cuerpo

    # ----- SENTENCIA IF -----
    def p_if_stmt(self, p):
        """if_stmt : IF expression COLON NEWLINE INDENT block_stmts DEDENT elif_chain else_clause
                   | IF expression COLON NEWLINE INDENT block_stmts DEDENT elif_chain
                   | IF expression COLON NEWLINE INDENT block_stmts DEDENT else_clause
                   | IF expression COLON NEWLINE INDENT block_stmts DEDENT"""
        condition = p[2]
        then_body = p[6]
        
        if len(p) == 10:  # if-elif-else
            p[0] = ("if_stmt", condition, then_body, p[8], p[9])
        elif len(p) == 9:
            if isinstance(p[8], list):  # if-elif
                p[0] = ("if_stmt", condition, then_body, p[8], None)
            else:  # if-else
                p[0] = ("if_stmt", condition, then_body, [], p[8])
        else:  # solo if
            p[0] = ("if_stmt", condition, then_body, [], None)

    # Cadena elif
    def p_elif_chain(self, p):
        """elif_chain : elif_chain elif_clause
                      | elif_clause"""
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = [p[1]]

    def p_elif_clause(self, p):
        """elif_clause : ELIF expression COLON NEWLINE INDENT block_stmts DEDENT"""
        p[0] = ("elif", p[2], p[6])

    # Cláusula else
    def p_else_clause(self, p):
        """else_clause : ELSE COLON NEWLINE INDENT block_stmts DEDENT"""
        p[0] = ("else", p[5])

    # ----- BUCLE WHILE -----
    def p_while_stmt(self, p):
        """while_stmt : WHILE expression COLON NEWLINE INDENT block_stmts DEDENT"""
        p[0] = ("while", p[2], p[6])

    # ----- BUCLE FOR -----
    def p_for_stmt(self, p):
        """for_stmt : FOR ID IN expression COLON NEWLINE INDENT block_stmts DEDENT"""
        p[0] = ("for", p[2], p[4], p[8])    # ----- SENTENCIAS SIMPLES -----
    def p_simple_stmt(self, p):
        """simple_stmt : small_stmt NEWLINE
                      | small_stmt"""
        p[0] = p[1]

    def p_small_stmt(self, p):
        """small_stmt : assignment
                     | aug_assignment
                     | expression
                     | return_stmt
                     | pass_stmt
                     | break_stmt
                     | continue_stmt"""
        p[0] = p[1]

    # Asignación simple
    def p_assignment(self, p):
        """assignment : ID ASSIGN expression
                     | ID ASSIGN_COLON expression"""
        p[0] = ("assignment", p[1], p[3])

    # Asignación aumentada
    def p_aug_assignment(self, p):
        """aug_assignment : ID PLUS_ASSIGN expression
                         | ID MINUS_ASSIGN expression
                         | ID MULTI_ASSIGN expression
                         | ID DIVIDE_ASSIGN expression
                         | ID MOD_ASSIGN expression
                         | ID FLOORDIV_ASSIGN expression
                         | ID POW_ASSIGN expression"""
        p[0] = ("aug_assignment", p[2], p[1], p[3])

    # Sentencias de control de flujo
    def p_return_stmt(self, p):
        """return_stmt : RETURN expression
                      | RETURN"""
        if len(p) == 3:
            p[0] = ("return", p[2])
        else:
            p[0] = ("return", None)

    def p_pass_stmt(self, p):
        """pass_stmt : PASS"""
        p[0] = ("pass",)

    def p_break_stmt(self, p):
        """break_stmt : BREAK"""
        p[0] = ("break",)

    def p_continue_stmt(self, p):
        """continue_stmt : CONTINUE"""
        p[0] = ("continue",)

    # ----- EXPRESIONES -----
    def p_expression(self, p):
        """expression : or_expression"""
        p[0] = p[1]

    # Operadores lógicos
    def p_or_expression(self, p):
        """or_expression : or_expression OR and_expression
        | and_expression"""
        p[0] = self._bin("OR", p[1], p[3]) if len(p) == 4 else p[1]

    def p_and_expression(self, p):
        """and_expression : and_expression AND not_expression
        | not_expression"""
        p[0] = self._bin("AND", p[1], p[3]) if len(p) == 4 else p[1]

    def p_not_expression(self, p):
        """not_expression : NOT not_expression
        | comparison"""
        p[0] = self._un("NOT", p[2]) if len(p) == 3 else p[1]

    # Operadores de comparación
    def p_comparison(self, p):
        """comparison : arithmetic_expr comp_op arithmetic_expr
                     | arithmetic_expr"""
        if len(p) == 4:
            p[0] = ("comparison", p[2], p[1], p[3])
        else:
            p[0] = p[1]

    def p_comp_op(self, p):
        """comp_op : LESS
                  | GREATER
                  | LESSEQ
                  | GREATEREQ
                  | EQ
                  | NEQ"""
        p[0] = p[1]

    # Expresiones aritméticas
    def p_arithmetic_expr(self, p):
        """arithmetic_expr : arithmetic_expr PLUS term
        | arithmetic_expr MINUS term
        | term"""
        if len(p) == 4:
            p[0] = ("binop", p[2], p[1], p[3])
        else:
            p[0] = p[1]

    def p_term(self, p):
        """term : term MULTI factor
        | term DIVIDE factor
        | term FLOORDIV factor
        | term MOD factor
        | factor"""
        if len(p) == 4:
            p[0] = ("binop", p[2], p[1], p[3])
        else:
            p[0] = p[1]

    def p_factor(self, p):
        """factor : PLUS factor %prec UPLUS
        | MINUS factor %prec UMINUS
        | power"""
        if len(p) == 3:
            p[0] = ("unaryop", p[1], p[2])
        else:
            p[0] = p[1]

    def p_power(self, p):
        """power : primary POW power
        | primary"""
        p[0] = self._bin("POW", p[1], p[3]) if len(p) == 4 else p[1]

    # ----- Primarios: literales, id, llamadas, listas/tuplas/dicts, agrupación -----

    # Llamadas a funciones con argumentos posicionales
    def p_primary_call(self, p):
        """primary : ID LPAREN arglist_opt RPAREN"""
        p[0] = ("call", self._id(p[1]), p[3])

    # Literales y nombres
    def p_primary_atoms(self, p):
        """primary : ID
        | INTEGER
        | DECIMAL
        | SCONST
        | TRUE
        | FALSE"""
        tok = p.slice[1].type
        if tok == "ID":
            p[0] = self._id(p[1])
        elif tok == "INTEGER":
            p[0] = self._lit("int", p[1])
        elif tok == "DECIMAL":
            p[0] = self._lit("float", p[1])
        elif tok == "SCONST":
            p[0] = self._lit("string", p[1])
        elif tok == "TRUE":
            p[0] = self._lit("bool", True)
        elif tok == "FALSE":
            p[0] = self._lit("bool", False)

    # Agrupación: (expr)
    def p_primary_group(self, p):
        """primary : LPAREN expression RPAREN"""
        p[0] = ("group", p[2])

    # Tuplas: (a,) — tupla de un elemento
    def p_primary_tuple_trailing(self, p):
        """primary : LPAREN expression COMMA RPAREN"""
        p[0] = ("tuple", [p[2]])

    # Tuplas: (a, b, ...)
    def p_primary_tuple(self, p):
        """primary : LPAREN expr_list COMMA_opt RPAREN"""
        if len(p[2]) > 1 or p[3] is True:
            p[0] = ("tuple", p[2])
        else:
            p[0] = ("group", p[2][0])

    # Listas: [a, b, c]
    def p_primary_list(self, p):
        """primary : LBRACKET expr_list_opt RBRACKET"""
        p[0] = ("list", p[2])

    # Diccionarios: {k1: v1, k2: v2}
    def p_primary_dict(self, p):
        """primary : LKEY key_value_list_opt RKEY"""
        p[0] = ("dict", p[2])

    # ----- utilidades para listas/argumentos -----
    def p_arglist_opt(self, p):
        """arglist_opt : expr_list_opt"""
        p[0] = p[1]

    def p_expr_list(self, p):
        """expr_list : expression
        | expr_list COMMA expression"""
        p[0] = p[1] + [p[3]] if len(p) == 4 else [p[1]]

    def p_expr_list_opt(self, p):
        """expr_list_opt : expr_list
        | empty"""
        p[0] = p[1] if p[1] is not None else []

    def p_COMMA_opt(self, p):
        """COMMA_opt : COMMA
        | empty"""
        p[0] = True if len(p) == 2 and p.slice[1].type == "COMMA" else False

    # Pares k:v para diccionarios
    def p_key_value(self, p):
        """key_value : expression COLON expression"""
        p[0] = (p[1], p[3])

    def p_key_value_list(self, p):
        """key_value_list : key_value
        | key_value_list COMMA key_value"""
        p[0] = p[1] + [p[3]] if len(p) == 4 else [p[1]]

    def p_key_value_list_opt(self, p):
        """key_value_list_opt : key_value_list
        | empty"""
        p[0] = p[1] if p[1] is not None else []

    # Vacío (utilidad)
    def p_empty(self, p):
        """empty :"""
        pass

    # Manejo de errores
    def p_error(self, p):
        if p:
            self.errors.append(
                Error(
                    f"Syntax error at token '{p.value}' ({p.type})",
                    p.lineno,
                    p.lexpos,
                    "parser",
                    self.lexer.data if hasattr(self.lexer, 'data') else "",
                )
            )
            # Intenta recuperarse del error
            self.parser.errok()
        else:
            self.errors.append(
                Error(
                    "Unexpected end of input", 
                    -1, 
                    -1, 
                    "parser", 
                    self.lexer.data if hasattr(self.lexer, 'data') else ""
                )
            )

# --- Tester ---
if __name__ == "__main__":
    errors = []
    parser = Parser(errors, debug=False)

    with open("test.py", "r", encoding="utf-8") as f:
        code = f.read()

    # Guardar el código para manejo de errores
    parser.lexer.data = code

    result = parser.parser.parse(code, lexer=parser.lexer.lex)

    print("AST result:", result)

    if errors:
        print("\nDetected errors:")
        for e in errors:
            print(e)
    else:
        print("\nNo syntax errors detected.")


# To test the parser

# Function to read the file and test the parser
def parser_tester(path, parser_instance):
    parser_instance.lexer.lex.lineno = 1  # reset line count
    stdout_original = sys.stdout
    
    # Reading the file
    with open(path, 'r', encoding='utf-8') as f:
        input_text = f.read()

    # Redirecting stdout to a report file
    with open("Parser_report.txt", "w", encoding="utf-8") as archivoParser:
        sys.stdout = archivoParser
        try:
            result = parser_instance.parser.parse(
                input_text,
                lexer=parser_instance.lexer.lex,
                debug=False
            )
            print("Parser completado exitosamente")
            print("AST result:", result)
            success = True
        except Exception as e:
            print(f"Error durante el parseo: {e}")
            success = False

    # Restoring stdout
    sys.stdout = stdout_original
    return success


# Structures testing method
def structures_parser_tester(errors):
    # Filtrar solo errores
    print(f"Se encontraron {len(errors)} errores durante el análisis sintáctico.")
    
    # Exportar a JSON
    logs_json = json.dumps([str(e) for e in errors], indent=4, ensure_ascii=False) 
    with open("logs.json", "w", encoding="utf-8") as f:
        f.write(logs_json)


# --- MAIN TEST ---
if __name__ == "__main__":
    errors = []
    parser_instance = Parser(errors, debug=False)

    # Archivo a analizar
    path = "test.py"
    success = parser_tester(path, parser_instance)

    structures_parser_tester(errors)