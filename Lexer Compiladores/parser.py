import ply.yacc as yacc
import sys
from Lexer import Lexer
from utils import Error
import ast
import json

# PLY necesita 'tokens' visible desde el módulo cuando se construye el parser
tokens = Lexer.tokens


class Parser:

    precedence = (
        ("left", "OR"),
        ("left", "AND"),
        ("right", "NOT"),
        (
            "nonassoc",
            "LESS",
            "LESSEQ",
            "GREATER",
            "GREATEREQ",
            "EQ",
            "NEQ",
            "LESSGREATER",
        ),
        ("left", "PLUS", "MINUS"),
        ("left", "MULTI", "DIVIDE", "FLOORDIV", "MOD"),
        ("right", "POW"),
        ("right", "UMINUS", "UPLUS"),
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

    # RECORDAR QUE LAS REGLAS DEBEN ESTAR EN ORDEN DESCENDENTE DE PRECEDENCIA

    # Programa: lista de sentencias (puede ser función, clase o expresión simple)
    def p_program(self, p):
        """program : top_level_stmt_list"""
        p[0] = ("program", p[1]) # AST raíz: tipo 'program', con lista de sentencias

    # Lista de sentencias: Se meten todas las sentencias de alto nivel en una lista de manera recursiva
    def p_stmt_list(self, p):
        """top_level_stmt_list : top_level_stmt_list top_level_stmt
                               | top_level_stmt"""
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = [p[1]]

    # Sentencias de alto nivel: puede ser funciones, clases o expresiones simples
    def p_stmt(self, p):
        """top_level_stmt : func_def
                          | class_def
                          | simple_stmt"""
        p[0] = p[1]

    # Definición de funciones -> Falta agregar parámetros
    def p_func_def(self, p):
        """func_def : DEF ID LPAREN RPAREN COLON NEWLINE INDENT body_stmt_list DEDENT"""
        p[0] = ("func_def", p[2], p[8])  # nombre, cuerpo

    # Definición de clases -> Falta agregar herencia y parámetros
    def p_class_def(self, p):
        """class_def : CLASS ID COLON NEWLINE INDENT body_stmt_list DEDENT"""
        p[0] = ("class_def", p[2], p[6])  # nombre, cuerpo

    # Cuerpo de funciones/clases (NO pueden contener def ni class) -----
    def p_body_stmt_list(self, p): 
        """body_stmt_list : body_stmt_list body_stmt
                          | body_stmt"""
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = [p[1]]

    # Sentencias permitidas dentro de funciones/clases
    def p_body_stmt(self, p):
        """body_stmt : if_stmt 
                     | assignment_stmt
                     | while_stmt
                     | for_stmt
                     | return_stmt
                     | simple_stmt""" # -> Recordar agregar un expression_stmt para llamado a funciones y demás. Puede que no sea necesario
        p[0] = p[1]

    # Sentencia if (simplificada, sin elif ni else) -> Preguntarle a Valentino si le vamos a agregar elif
    def p_if_stmt(self, p):
        """if_stmt : IF expression COLON NEWLINE INDENT body_stmt_list DEDENT
                   | IF expression COLON NEWLINE INDENT body_stmt_list DEDENT ELSE COLON NEWLINE INDENT body_stmt_list DEDENT"""
        if len(p) == 8:
            # if sin else
            p[0] = ("if", p[2], p[6], None)
        else:
            # if con else
            p[0] = ("if", p[2], p[6], p[12])

    # Sentencia de asignación (identificador = expresión)
    def p_assignment_stmt(self, p): # -> preguntarle a Valentino si se va a agregar := (morsa) por su sintaxis especial
        """assignment_stmt : ID ASSIGN expression
                           | ID PLUS_ASSIGN expression
                           | ID MINUS_ASSIGN expression
                           | ID MULTI_ASSIGN expression
                           | ID DIVIDE_ASSIGN expression
                           | ID MOD_ASSIGN expression
                           | ID FLOORDIV_ASSIGN expression
                           | ID POW_ASSIGN expression """
        # Conservamos la forma original de AST para no romper consumidores no relacionados
        p[0] = ("assign", p[1], p[3])

    # Sentencia while
    def p_while_stmt(self, p):
        """while_stmt : WHILE expression COLON NEWLINE INDENT body_stmt_list DEDENT"""
        p[0] = ("while", p[2], p[6])

    # Sentencia for -> Preguntarle a Valentino si le vamos a agregar range, foreach y demás
    def p_for_stmt(self, p):
        """for_stmt : FOR ID IN expression COLON NEWLINE INDENT body_stmt_list DEDENT"""
        p[0] = ("for", p[2], p[6])

    # Sentencia return
    def p_return_stmt(self, p):
        """return_stmt : RETURN expression
                       | RETURN """
        if len(p) == 3:
            p[0] = ("return", p[2])
        else:
            p[0] = ("return", None)

    # ----- Sentencia simple como sentencia de expresión -----
    # Minimiza cambios: ahora simple_stmt acepta cualquier expresión
    def p_simple_stmt(self, p):
        """simple_stmt : expression"""
        p[0] = ("expr", p[1])

    # ======================
    # ===== Expresiones =====
    # ======================

    def p_expression(self, p):
        """expression : or_expression"""
        p[0] = p[1]

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

    def p_comparison(self, p):
        """comparison : arithmetic_expression
        | arithmetic_expression comparator arithmetic_expression"""
        p[0] = self._bin(p[2], p[1], p[3]) if len(p) == 4 else p[1]

    def p_comparator(self, p):
        """comparator : EQ
        | NEQ
        | LESS
        | LESSEQ
        | GREATER
        | GREATEREQ
        | LESSGREATER"""
        p[0] = p.slice[1].type

    def p_arithmetic_expression(self, p):
        """arithmetic_expression : arithmetic_expression PLUS term
        | arithmetic_expression MINUS term
        | term"""
        p[0] = self._bin(p.slice[2].type, p[1], p[3]) if len(p) == 4 else p[1]

    def p_term(self, p):
        """term : term MULTI factor
        | term DIVIDE factor
        | term FLOORDIV factor
        | term MOD factor
        | factor"""
        p[0] = self._bin(p.slice[2].type, p[1], p[3]) if len(p) == 4 else p[1]

    def p_factor(self, p):
        """factor : PLUS factor %prec UPLUS
        | MINUS factor %prec UMINUS
        | power"""
        if len(p) == 3:
            p[0] = self._un(p.slice[1].type, p[2])
        else:
            p[0] = p[1]

    def p_power(self, p):
        """power : primary
        | primary POW power"""
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
                    f"Syntax error at token '{p.value}'",
                    p.lineno,
                    p.lexpos,
                    "parser",
                    self.lexer.data,
                )
            )
        else:
            self.errors.append(
                Error("Unexpected end of input", -1, -1, "parser", self.lexer.data)
            )


# Tester
if __name__ == "__main__":
    errors = []
    parser = Parser(errors, debug=False)

    with open("test.py", "r", encoding="utf-8") as f:
        code = f.read()

    result = parser.parser.parse(code, lexer=parser.lexer.lex)

    print("AST result:", result)

    if errors:
        print("Detected errors:")
        for e in errors:
            print(e)
    else:
        print("No syntax errors detected.")


# ---- To test the parser ----

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
    path = "original_text.py"
    success = parser_tester(path, parser_instance)

    structures_parser_tester(errors)
