import ply.yacc as yacc
import sys
from Lexer import Lexer
from utils import Error
import ast
import json

# TODO(VAL): Agregar regla de inline function (def f(): return 0)
# TODO(EMMA): keyword args (e.g. print(msg="hello"))

class Parser:
    # ----- PRECEDENCIA Y ASOCIATIVIDAD -----
    precedence = (
        ("left", "OR"),  # OR tiene menor precedencia
        ("left", "AND"),
        ("right", "NOT"),
        ("left", "LESS", "GREATER", "LESSEQ", "GREATEREQ", "EQ", "NEQ"),
        ("left", "PLUS", "MINUS"),
        ("left", "MULTI", "DIVIDE", "FLOORDIV", "MOD"),
        (
            "right",
            "UMINUS",
            "UPLUS",
        ),  # Operadores unarios
        ("right", "POW"),  # POW tiene mayor precedencia
    )

    def __init__(self, errors: list[Error], debug=False):
        self.errors = errors
        self.debug = debug
        self.lexer = Lexer(errors, debug)
        self.lexer.build()
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self, start="program", debug=debug)

    # --- Crean nodos del Abstract Syntax Tree (AST).

    def _bin(self, op, left, right):
        return ("binary_op", op.lower(), left, right)

    def _un(self, op, operand):
        return ("unary_op", op.lower(), operand)

    def _lit(self, kind, value):
        return ("literal", kind, value)

    def _self(self, name):
        return ("self_identifier", name)

    def _id(self, name):
        return ("identifier", name)

    def _cmp_chain(self, left, chain):
        """chain is a list of (op_token, expr)."""
        return ("cmp_chain", left, chain)

    # --- diagnostics ---------------------------------------------------------
    def _has_lexer_errors(self) -> bool:
        """Return True if any error originated in the lexer."""
        return any(getattr(e, "source", "").lower() == "lexer" for e in self.errors)

    def _has_parser_errors(self) -> bool:
        """Return True if any error originated in the parser."""
        return any(getattr(e, "source", "").lower() == "parser" for e in self.errors)

    def _validate_ast_for_empty_string_literals(self, node):
        """
        Walk the AST and emit a validator warning if we find ('literal','string','').
        This is especially suspicious when lexer errors occurred (e.g., broken strings).
        """
        def walk(n):
            if isinstance(n, tuple):
                # ('literal', 'string', '')
                if len(n) == 3 and n[0] == "literal" and n[1] == "string" and n[2] == "":
                    # Attach a validator entry (non-blocking) to the shared errors list
                    self.errors.append(
                        Error(
                            "Empty string literal found in AST; likely caused by prior lexing errors on string tokens.",
                            getattr(self.lexer, "lineno", -1),
                            -1,
                            "validator",
                            self.lexer.data if hasattr(self.lexer, "data") else "",
                        )
                    )
                for part in n:
                    walk(part)
            elif isinstance(n, list):
                for item in n:
                    walk(item)
            # identifiers/ints/floats/None are leaves; ignore

        walk(node)

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
    # ----- SENTENCIAS DE NIVEL SUPERIOR (módulo) -----
    def p_top_level_stmt(self, p):
        """top_level_stmt : func_def
                          | class_def
                          | simple_stmt
                          | if_stmt
                          | while_stmt
                          | for_stmt
                          | try_stmt"""
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
                          | for_stmt
                          | try_stmt"""
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

    # ----- SENTENCIAS DENTRO DE BLOQUES DE CONTROL -----
    def p_block_stmt(self, p):
        """block_stmt : simple_stmt
        | if_stmt
        | while_stmt
        | for_stmt
        | try_stmt"""
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
    def p_params_list(self, p): # Falta separar self de ID sin self.x para atributos en definición de métodos
        """params_list : params_list COMMA nested_id
                       | nested_id
                       | params_list COMMA ID
                       | ID """
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]

    # ----- DEFINICIÓN DE CLASES -----
    def p_class_def(self, p):
        """class_def : CLASS ID COLON NEWLINE INDENT class_body_stmts DEDENT
                     | CLASS ID LPAREN params_list RPAREN COLON NEWLINE INDENT class_body_stmts DEDENT"""
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
        """for_stmt : FOR target_tuple IN expression COLON NEWLINE INDENT block_stmts DEDENT
        | FOR target IN expression COLON NEWLINE INDENT block_stmts DEDENT"""
        # for a, b in iterable:
        #     body
        # o
        # for x in iterable:
        #     body
        target = p[2]
        iterable = p[4]
        body = p[8]
        p[0] = ("for", target, iterable, body)

    # ----- SENTENCIAS SIMPLES -----

    # Sentencia simple dentro de clase
    def p_simple_stmt(self, p):
        """simple_stmt : small_stmt NEWLINE
                       | small_stmt"""
        p[0] = p[1]

    # ----- SENTENCIAS SIMPLES -----
    def p_small_stmt(self, p):
        """small_stmt : assignment
        | aug_assignment
        | expression
        | return_stmt
        | pass_stmt
        | break_stmt
        | continue_stmt
        | print_stmt"""
        p[0] = p[1]

    # ----- TARGET LIST (para unpacking) -----
    # Un "target" puede ser un ID simple o una lista de targets
    def p_target(self, p):
        """target : ID
        | nested_id"""
        # Un target simple: variable o atributo (self.x, obj.attr)
        p[0] = p[1]

    # Lista de targets para unpacking: a, b, c
    def p_target_list(self, p):
        """target_list : target_list COMMA target
        | target COMMA target"""
        # target_list : a, b, c
        # Resultado: ("target_list", [a, b, c])
        if len(p) == 4:
            if isinstance(p[1], tuple) and p[1][0] == "target_list":
                # Ya es una lista, agregar el nuevo target
                p[0] = ("target_list", p[1][1] + [p[3]])
            else:
                # Primer par: a, b
                p[0] = ("target_list", [p[1], p[3]])

    # Target con paréntesis opcionales: (a, b) o a, b
    def p_target_tuple(self, p):
        """target_tuple : LPAREN target_list RPAREN
        | target_list"""
        # (a, b, c) o simplemente a, b, c
        if len(p) == 4:
            # Con paréntesis
            p[0] = p[2]
        else:
            # Sin paréntesis
            p[0] = p[1]

    # ----- SENTENCIA PRINT -----
    def p_print_stmt(self, p):
        """print_stmt : PRINT LPAREN expr_list_opt RPAREN
        | PRINT LPAREN RPAREN"""
        # PRINT puede recibir múltiples argumentos separados por coma
        # PRINT(a, b, c) → ("print", [a, b, c])
        # PRINT() → ("print", [])
        if len(p) == 5:
            p[0] = ("print", p[3])  # p[3] es la lista de expresiones
        else:
            p[0] = ("print", [])

    # ----- BLOQUE TRY-EXCEPT -----
    def p_try_stmt(self, p):
        """try_stmt : TRY COLON NEWLINE INDENT block_stmts DEDENT except_clauses
        | TRY COLON NEWLINE INDENT block_stmts DEDENT"""
        # try:
        #     <block_stmts>
        # except ExceptionType:
        #     <handler>
        # except:
        #     <default_handler>

        try_body = p[5]  # Cuerpo del try

        if len(p) == 8:
            # Con cláusulas except
            except_clauses = p[7]  # Lista de excepts
            p[0] = ("try_stmt", try_body, except_clauses)
        else:
            # Try sin except (poco común pero válido en algunos lenguajes)
            p[0] = ("try_stmt", try_body, [])

    # ----- CLÁUSULAS EXCEPT (Una o más) -----
    def p_except_clauses(self, p):
        """except_clauses : except_clauses except_clause
        | except_clause"""
        # Permite múltiples excepts: except E1: ... except E2: ...
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = [p[1]]

    # ----- CLÁUSULA EXCEPT INDIVIDUAL -----
    def p_except_clause(self, p):
        """except_clause : EXCEPT ID COLON NEWLINE INDENT block_stmts DEDENT
        | EXCEPT COLON NEWLINE INDENT block_stmts DEDENT"""
        # except ExceptionType:
        #     <handler_body>
        # o
        # except:  (captura todo)
        #     <default_handler>

        if len(p) == 8:
            # except con tipo de excepción específico
            exception_type = p[2]
            handler_body = p[6]
            p[0] = ("except", exception_type, handler_body)
        else:
            # except genérico (sin tipo)
            handler_body = p[5]
            p[0] = ("except", None, handler_body)

    # Asignación simple
    def p_assignment(self, p):
        """assignment : target_tuple ASSIGN expression
        | target_tuple ASSIGN_COLON expression
        | nested_id ASSIGN expression
        | nested_id ASSIGN_COLON expression
        | ID ASSIGN expression
        | ID ASSIGN_COLON expression"""
        # a, b = 1, 2
        # x = 5
        # self.attr = 10
        p[0] = ("assignment", p[1], p[3])

    # nested ids (id.id.id ...)
    def p_nested_id(self, p):
        """nested_id : nested_id DOT ID
                     | ID DOT ID"""
        if len(p) == 4:
            p[0] = ("attribute_access", p[1], p[3])  # (obj, attr)
        else:
            p[0] = ("attribute_access", p[1], p[3])  # (obj.attr, attr)

    # Asignación aumentada
    def p_aug_assignment(self, p):
        """aug_assignment : nested_id PLUS_ASSIGN expression
        | nested_id MINUS_ASSIGN expression
        | nested_id MULTI_ASSIGN expression
        | nested_id DIVIDE_ASSIGN expression
        | nested_id MOD_ASSIGN expression
        | nested_id FLOORDIV_ASSIGN expression
        | nested_id POW_ASSIGN expression
        | ID PLUS_ASSIGN expression
        | ID MINUS_ASSIGN expression
        | ID MULTI_ASSIGN expression
        | ID DIVIDE_ASSIGN expression
        | ID MOD_ASSIGN expression
        | ID FLOORDIV_ASSIGN expression
        | ID POW_ASSIGN expression"""
        # NOTE: Augmented assignments NO soportan unpacking
        # a, b += 1  → INVÁLIDO en Python
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

    """ Según precedencia y asociatividad definidas arriba, la jerarquía es:
    
        expression
        └── tuple_expr (opt)
            └── or_expression
                └── and_expression
                    └── not_expression
                            └── comparison
                                    └── arithmetic_expr
                                        └── term
                                            └── factor
                                                    └── power
                                                        └── primary
    """

    def p_expression(self, p):
        """expression : tuple_expr"""
        p[0] = p[1]

    def p_tuple_expr(self, p):
        """tuple_expr : or_expression COMMA or_expression
        | tuple_expr COMMA or_expression
        | or_expression"""
        # a, b → ("tuple", [a, b])
        # a, b, c → ("tuple", [a, b, c])
        # a → a (sin cambio)
        if len(p) == 2:
            # Solo una expresión, no es tupla
            p[0] = p[1]
        elif len(p) == 4:
            # Expresión con comas
            if isinstance(p[1], tuple) and p[1][0] == "tuple":
                # Ya es una tupla, agregar elemento
                p[0] = ("tuple", p[1][1] + [p[3]])
            else:
                # Primera tupla: a, b
                p[0] = ("tuple", [p[1], p[3]])

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

    # Chained comparison: a < b < c == (a < b) and (b < c)
    """
    split the comparison so it collects a list of pairs after the first expression
    first part --> "left"
    second part --> "chain" := zero or more (op, expression) pairs

    gramática:

    comparison  → arithmetic_expr comp_chain
    comp_chain  → ε
                | comp_op arithmetic_expr
                | comp_chain comp_op arithmetic_expr

    ejemplo:
    a < b → ("comparison", "<", a, b)
    a < b < c → ("cmp_chain", a, [("<", b), ("<", c)])
    a < b <= c != d → ("cmp_chain", a, [("<", b), ("<=", c), ("!=", d)])

    ejemplo 2:
    x + 1 < y*2 < z**3
        left: (x+1)
        chain: ("<", y*2), ("<", z**3)       
    """
    # comparison := arithmetic_expr (comp_op arithmetic_expr)*
    def p_comparison(self, p):
        """comparison : arithmetic_expr comp_chain"""
        left = p[1]
        chain = p[2]  # list of (op, expr)
        if not chain:
            # No comparison at all → just the arithmetic expr (e.g., "a+1")
            p[0] = left
        elif len(chain) == 1:
            # Backward-compatible for existing code/tests:
            op, right = chain[0]
            p[0] = ("comparison", op, left, right)
        else:
            # True chained comparison
            p[0] = self._cmp_chain(left, chain)

    def p_comp_chain(self, p):
        """comp_chain : comp_chain comp_op arithmetic_expr
                    | comp_op arithmetic_expr
                    | empty"""
        if len(p) == 2:
            # empty
            p[0] = []
        elif len(p) == 3:
            # first pair
            p[0] = [(p[1], p[2])]
        else:
            # extend
            p[0] = p[1] + [(p[2], p[3])]

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
        """primary : nested_id
                   | ID
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

    # Tuplas con paréntesis: (a, b) o (a,)
    def p_primary_tuple_explicit(self, p):
        """primary : LPAREN tuple_expr RPAREN
        | LPAREN tuple_expr COMMA RPAREN"""
        # (a, b, c) → ya es ("tuple", [...])
        # (a,) → ("tuple", [a])
        if len(p) == 4:
            # (a, b, c)
            if isinstance(p[2], tuple) and p[2][0] == "tuple":
                p[0] = p[2]  # Ya es tupla
            else:
                # (a) → grouping, no tupla
                p[0] = ("group", p[2])
        else:
            # (a,) → tupla de un elemento
            if isinstance(p[2], tuple) and p[2][0] == "tuple":
                p[0] = p[2]
            else:
                p[0] = ("tuple", [p[2]])

    # Listas: [a, b, c] y [a, b,]
    def p_primary_list(self, p):
        """primary : LBRACKET expr_list_opt RBRACKET
                    | LBRACKET expr_list COMMA RBRACKET """
        p[0] = ("list", p[2])

    # Diccionarios: {k1: v1, k2: v2}  and  {k1: v1,}
    def p_primary_dict(self, p):
        """primary : LKEY key_value_list_opt RKEY
                | LKEY key_value_list COMMA RKEY"""
        # p[2] is always the list of pairs (possibly [])
        p[0] = ("dict", p[2])

    # ----- utilidades para listas/argumentos -----
    def p_arglist_opt(self, p):
        """arglist_opt : expr_list_opt"""
        p[0] = p[1]

    def p_expr_list(self, p):
        """expr_list : expr_list COMMA ID ASSIGN expression
                     | expr_list COMMA nested_id ASSIGN expression
                     | expr_list COMMA expression
                     | ID ASSIGN expression
                     | nested_id ASSIGN expression
                     | expression"""
        p[0] = p[1] + [p[3]] if len(p) == 4 else [p[1]]

    def p_expr_list_opt(self, p):
        """expr_list_opt : expr_list
                         | empty"""
        p[0] = p[1] if p[1] is not None else []

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

def _line_info_from_lexpos(text: str, lexpos: int):
    """Return (line_text, col0, col1) given a 0-based lexpos; handles EOF/unknown."""
    if lexpos is None or lexpos < 0 or not text:
        return ("", -1, -1)
    start = text.rfind("\n", 0, lexpos) + 1
    end = text.find("\n", lexpos)
    if end == -1:
        end = len(text)
    line = text[start:end]
    col0 = lexpos - start
    return (line, col0, col0 + 1)

def format_error_pretty(e, source_code: str):
    """Pretty, caret-annotated error line."""
    try:
        line, col0, _ = _line_info_from_lexpos(source_code, getattr(e, "lexpos", -1))
        lineno = getattr(e, "lineno", -1)
        msg = getattr(e, "message", str(e))
        caret = (" " * col0 + "^") if col0 >= 0 else ""
        return f"L{lineno}:{(col0+1) if col0>=0 else '?'}  {msg}\n    {line}\n    {caret}"
    except Exception:
        # Fallback
        return str(e)

def run_single_file(path: str):
    """Parse one file with a fresh Parser; return a rich dict for reporting."""
    # Fresh container for this run
    errors: list[Error] = []
    parser = Parser(errors, debug=False)

    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

    # Give the lexer the source for better locations
    parser.lexer.data = code
    # (If your Lexer has more state like indent stack, ensure it’s reset here; fresh Parser usually suffices)

    result = None
    uncaught = None
    try:
        # IMPORTANT: use the *fresh* lex object bound to this parser instance
        parser.lexer.lex.lineno = 1
        result = parser.parser.parse(code, lexer=parser.lexer.lex, debug=False)

        # Optional AST post-check when lexer had errors
        if result is not None and parser._has_lexer_errors():
            parser._validate_ast_for_empty_string_literals(result)

    except Exception as ex:
        uncaught = str(ex)

    # Decide success more strictly
    has_lex_err = parser._has_lexer_errors()
    has_par_err = parser._has_parser_errors()
    success = (result is not None) and not (has_lex_err or has_par_err) and (uncaught is None)

    # Pretty-errors for report
    pretty_errors = [format_error_pretty(e, code) for e in errors]

    return {
        "path": path,
        "success": success,
        "result": None if not success else result,  # keep report light
        "error_count": len(errors),
        "has_lexer_errors": has_lex_err,
        "has_parser_errors": has_par_err,
        "uncaught": uncaught,
        "errors_pretty": pretty_errors,
        "errors_raw": [str(e) for e in errors],
    }

# --- MAIN TEST ---
if __name__ == "__main__":
    test_files = [
        "tests/parser_assign_expr.py",
        "tests/parser_augmented_assigns.py",
        "tests/parser_chained_comparison.py",
        "tests/parser_class_and_method.py",
        "tests/parser_dict_trailing_comma.py",
        "tests/parser_function_control.py",
        "tests/parser_inline_function.py",
        "tests/parser_keyword_args.py",
        "tests/parser_list_trailing_comma.py",
        "tests/parser_minimal.py",
        "tests/parser_missing_colon_or_indent.py",
        "tests/parser_semicolons.py",
        "tests/parser_top_level_if.py",
        "tests/parser_tuple_unpacking.py",
        "tests/parser_print_try.py",
        "tests/parser_params_and_calls.py",
    ]

    # Run
    reports = []
    for path in test_files:
        rep = run_single_file(path)
        reports.append(rep)

    # --- Write the human report (single place) ---
    with open("Parser_report.txt", "w", encoding="utf-8") as out:
        for rep in reports:
            out.write(f"=== {rep['path']} ===\n")
            status = "OK" if rep["success"] else "ERROR"
            out.write(f"Status: {status}\n")
            if rep["uncaught"]:
                out.write(f"Uncaught exception: {rep['uncaught']}\n")
            out.write(f"Lexer errors: {rep['has_lexer_errors']} | Parser errors: {rep['has_parser_errors']}\n")
            out.write(f"Total errors: {rep['error_count']}\n")
            if not rep["success"]:
                # Show the first few pretty errors with caret
                for msg in rep["errors_pretty"][:10]:
                    out.write(msg + "\n")
            else:
                out.write("AST: (omitted in report for brevity)\n")
            out.write("\n")

    # --- Write machine-readable logs once, not per file ---
    with open("logs.json", "w", encoding="utf-8") as jf:
        json.dump(reports, jf, indent=2, ensure_ascii=False)

    # Terminal summary (short)
    for rep in reports:
        status = "OK" if rep["success"] else "ERROR"
        print(f"{status:5}  {rep['error_count']:2}  {rep['path']}")
