import ply.yacc as yacc
import sys
from Lexer import Lexer
from utils import Error
import ast
import json



class Parser:
    def __init__(self, errors: list[Error], debug=False):
        self.errors = errors
        self.debug = debug
        self.lexer = Lexer(errors, debug)
        self.lexer.build()
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self, start="program", debug=debug)

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

    # Sentencia simple: puede ser un identificador, entero, decimal o cadena
    def p_simple_stmt(self, p):
        """simple_stmt : ID
                       | INTEGER
                       | DECIMAL
                       | SCONST"""
        p[0] = ("expr", p[1])

    # Placeholder para expresiones (puede ser una sentencia simple por ahora)
    def p_expression(self, p):
        """expression : simple_stmt"""
        p[0] = p[1]

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
        print("\nDetected errors:")
        for e in errors:
            print(e)
    else:
        print("\nNo syntax errors detected.")


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
    path = "test.py"
    success = parser_tester(path, parser_instance)

    structures_parser_tester(errors)