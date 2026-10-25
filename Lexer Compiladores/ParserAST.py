import ply.yacc as yacc
import sys
from Lexer import Lexer
from utils import Error
from ast_nodes import *
import json

class Parser:
    # ----- PRECEDENCIA Y ASOCIATIVIDAD -----
    precedence = (
        ("left", "OR"),
        ("left", "AND"),
        ("right", "NOT"),
        ("left", "LESS", "GREATER", "LESSEQ", "GREATEREQ", "EQ", "NEQ"),
        ("left", "PLUS", "MINUS"),
        ("left", "MULTI", "DIVIDE", "FLOORDIV", "MOD"),
        ("right", "UMINUS", "UPLUS"),
        ("right", "POW"),
    )

    def __init__(self, errors: list[Error], debug=False):
        self.errors = errors
        self.debug = debug
        self.lexer = Lexer(errors, debug)
        self.lexer.build()
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self, start="program", debug=debug)

    def _find_column(self, lexpos: int) -> int:
        """Compute 1-based column from absolute lexpos using the lexer's input buffer."""
        data = getattr(self.lexer, "data", None) or getattr(self.lexer, "lexdata", "")
        last_cr = data.rfind("\n", 0, lexpos)
        if last_cr < 0:
            last_cr = -1
        return (lexpos - last_cr)

    def _setpos(self, node: ASTNode, p, i: int):
        """Attach (lineno, col) from the i-th symbol of production p."""
        try:
            node.set_pos(p.lineno(i), self._find_column(p.lexpos(i)))
        except Exception:
            # Be forgiving if some productions don't expose lexpos/lineno
            pass
        return node

    def _block(self, stmts, p=None, i=None):
        """Wrap stmt list into BlockNode and optionally set position from p[i]."""
        b = BlockNode(stmts or [])
        if p is not None and i is not None:
            self._setpos(b, p, i)
        return b

    # --- diagnostics ---------------------------------------------------------
    def _has_lexer_errors(self) -> bool:
        for e in self.errors:
            src = getattr(e, "source", None)
            label = (str(src) if src is not None else "").strip().lower()
            if label == "lexer":
                return True
            s = str(e).lower()
            if "error(lexer)" in s:
                return True
        return False

    def _has_parser_errors(self) -> bool:
        for e in self.errors:
            src = getattr(e, "source", None)
            label = (str(src) if src is not None else "").strip().lower()
            if label == "parser":
                return True
            s = str(e).lower()
            if "error(parser)" in s:
                return True
        return False

    def _validate_ast_for_empty_string_literals(self, node):
        """Walk the AST and emit a validator warning if we find empty string literals."""
        def walk(n):
            if isinstance(n, LiteralNode):
                if n.kind == "string" and n.value == "":
                    self.errors.append(
                        Error(
                            "Empty string literal found in AST; likely caused by prior lexing errors.",
                            getattr(self.lexer, "lineno", -1),
                            -1,
                            "validator",
                            self.lexer.data if hasattr(self.lexer, "data") else "",
                        )
                    )
            elif isinstance(n, ASTNode):
                # Walk all attributes that might contain child nodes
                for attr_name in dir(n):
                    if attr_name.startswith('_'):
                        continue
                    attr = getattr(n, attr_name)
                    if isinstance(attr, list):
                        for item in attr:
                            walk(item)
                    elif isinstance(attr, ASTNode):
                        walk(attr)

        walk(node)

    # ----- Reglas de la gramática -----

    def p_program(self, p):
        """program : top_level_stmts"""
        p[0] = ProgramNode(p[1])

    # ----- SENTENCIAS DE NIVEL SUPERIOR (módulo) -----

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
                          | simple_stmt
                          | if_stmt
                          | while_stmt
                          | for_stmt
                          | try_stmt"""
        p[0] = p[1]

    # ----- SENTENCIAS DENTRO DE FUNCIONES -----

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
                      | for_stmt
                      | try_stmt"""
        p[0] = p[1]

    # ----- DEFINICIÓN DE FUNCIONES -----
    def p_func_def(self, p):
        """func_def : DEF ID LPAREN params_list RPAREN COLON func_suite
                    | DEF ID LPAREN RPAREN COLON func_suite"""
        if len(p) == 8:
            node = FuncDefNode(func_name=p[2], params=p[4], suite=p[7])
            p[0] = self._setpos(node, p, 1)
        else:
            node = FuncDefNode(func_name=p[2], params=[], suite=p[6])
            p[0] = self._setpos(node, p, 1)

    def p_params_list(self, p):
        """params_list : params_list COMMA param
                    | param"""
        if len(p) == 4:  # params_list COMMA param
            p[0] = p[1] + [p[3]]
        else:  # param
            p[0] = [p[1]]

    def p_param(self, p):
        """param : ID DOT ID ASSIGN expression
                | ID ASSIGN expression
                | ID DOT ID
                | ID"""
        if len(p) == 6:
            p[0] = (f"{p[1]}.{p[3]}", p[5])
        elif len(p) == 5:
            p[0] = (f"{p[1]}.{p[3]}", p[4])
        elif len(p) == 4:
            if p[2] == '.':
                p[0] = f"{p[1]}.{p[3]}"
            else:  # p[2] == '='
                p[0] = (p[1], p[3])
        elif len(p) == 2:
            p[0] = p[1]

    def p_func_suite_block(self, p):
        """func_suite : NEWLINE INDENT func_body_stmts DEDENT"""
        p[0] = self._block(p[3], p, 2)  # position from INDENT

    def p_func_suite_inline(self, p):
        """func_suite : simple_stmt"""
        p[0] = self._block([p[1]], p, 1)

    # ----- DEFINICIÓN DE CLASES -----
    def p_class_def(self, p):
        """class_def : CLASS ID COLON NEWLINE INDENT class_body_stmts DEDENT
                     | CLASS ID LPAREN params_list RPAREN COLON NEWLINE INDENT class_body_stmts DEDENT"""
        if len(p) == 8:
            body = self._block(p[6], p, 5)  # from INDENT
            node = ClassDefNode(class_name=p[2], parent=None, body=body)
            p[0] = self._setpos(node, p, 1)  # CLASS
        else:
            body = self._block(p[9], p, 8)
            node = ClassDefNode(class_name=p[2], parent=p[4], body=body)
            p[0] = self._setpos(node, p, 1)

    # ----- SENTENCIA IF -----
    def p_if_stmt(self, p):
        """if_stmt : IF expression COLON NEWLINE INDENT block_stmts DEDENT elif_chain else_clause
                   | IF expression COLON NEWLINE INDENT block_stmts DEDENT elif_chain
                   | IF expression COLON NEWLINE INDENT block_stmts DEDENT else_clause
                   | IF expression COLON NEWLINE INDENT block_stmts DEDENT"""
        condition = p[2]
        then_body = self._block(p[6], p, 1)  # position from IF

        if len(p) == 10:
            node = IfNode(condition, then_body, p[8], p[9])
        elif len(p) == 9:
            if isinstance(p[8], list):
                node = IfNode(condition, then_body, p[8], None)
            else:
                node = IfNode(condition, then_body, [], p[8])
        else:
            node = IfNode(condition, then_body, [], None)

        p[0] = self._setpos(node, p, 1)

    def p_elif_chain(self, p):
        """elif_chain : elif_chain elif_clause
                      | elif_clause"""
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = [p[1]]

    def p_elif_clause(self, p):
        """elif_clause : ELIF expression COLON NEWLINE INDENT block_stmts DEDENT"""
        block = self._block(p[6], p, 1)
        node = ElifNode(condition=p[2], body=block)
        p[0] = self._setpos(node, p, 1)

    def p_else_clause(self, p):
        """else_clause : ELSE COLON NEWLINE INDENT block_stmts DEDENT"""
        block = self._block(p[5], p, 1)
        node = ElseNode(body=block)
        p[0] = self._setpos(node, p, 1)

    # ----- BUCLE WHILE -----
    def p_while_stmt(self, p):
        """while_stmt : WHILE expression COLON NEWLINE INDENT block_stmts DEDENT"""
        block = self._block(p[6], p, 1)
        node = WhileNode(condition=p[2], body=block)
        p[0] = self._setpos(node, p, 1)

    # ----- BUCLE FOR -----
    def p_for_stmt(self, p):
        """for_stmt : FOR target_tuple IN expression COLON NEWLINE INDENT block_stmts DEDENT
                    | FOR target IN expression COLON NEWLINE INDENT block_stmts DEDENT"""
        block = self._block(p[8], p, 1)
        node = ForNode(target=p[2], iterable=p[4], body=block)
        p[0] = self._setpos(node, p, 1)

    # ----- SENTENCIAS SIMPLES -----
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
                      | continue_stmt
                      | print_stmt"""
        p[0] = p[1]

    # ----- TARGET LIST (para unpacking) -----
    def p_target(self, p):
        """target : ID
                  | nested_id"""
        p[0] = p[1]

    def p_target_list(self, p):
        """target_list : target_list COMMA target
                       | target COMMA target"""
        if len(p) == 4:
            if isinstance(p[1], TargetListNode):
                p[0] = TargetListNode(p[1].targets + [p[3]])
            else:
                p[0] = TargetListNode([p[1], p[3]])

    def p_target_trailing(self, p):
        """target_trailing : target COMMA"""
        p[0] = TargetListNode([p[1]])

    def p_target_tuple(self, p):
        """target_tuple : LPAREN target_list RPAREN
                        | LPAREN target COMMA RPAREN
                        | target_list
                        | target_trailing"""
        if len(p) == 4:
            p[0] = p[2]
        elif len(p) == 5:
            p[0] = TargetListNode([p[2]])
        else:
            p[0] = p[1]

    # ----- SENTENCIA PRINT -----
    def p_print_stmt(self, p):
        """print_stmt : PRINT LPAREN expr_list_plain_opt RPAREN
                      | PRINT LPAREN RPAREN"""
        if len(p) == 5:
            node = PrintNode(p[3])
            p[0] = self._setpos(node, p, 1)
        else:
            node = PrintNode([])
            p[0] = self._setpos(node, p, 1)

    # ----- BLOQUE TRY-EXCEPT -----
    def p_try_stmt(self, p):
        """try_stmt : TRY COLON NEWLINE INDENT block_stmts DEDENT except_clauses
                    | TRY COLON NEWLINE INDENT block_stmts DEDENT"""
        try_body = self._block(p[5], p, 1)
        if len(p) == 8:
            node = TryNode(try_body=try_body, except_clauses=p[7])
        else:
            node = TryNode(try_body=try_body, except_clauses=[])

        p[0] = self._setpos(node, p, 1)

    def p_except_clauses(self, p):
        """except_clauses : except_clauses except_clause
                          | except_clause"""
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = [p[1]]

    def p_except_clause(self, p):
        """except_clause : EXCEPT ID COLON NEWLINE INDENT block_stmts DEDENT
                         | EXCEPT COLON NEWLINE INDENT block_stmts DEDENT"""
        if len(p) == 8:
            handler_block = self._block(p[6], p, 1)
            node = ExceptNode(exception_type=p[2], handler_body=handler_block)
            p[0] = self._setpos(node, p, 1)
        else:
            handler_block = self._block(p[5], p, 1)
            node = ExceptNode(exception_type=None, handler_body=handler_block)
            p[0] = self._setpos(node, p, 1)

    # ----- ASIGNACIONES -----
    def p_assignment(self, p):
        """assignment : target_tuple ASSIGN tuple_expr
        | target_tuple ASSIGN_COLON tuple_expr
        | nested_id ASSIGN expression
        | nested_id ASSIGN_COLON expression
        | ID ASSIGN expression
        | ID ASSIGN_COLON expression
        | primary ASSIGN expression
        | primary ASSIGN_COLON expression"""
        # Aceptar también 'primary' como target para cubrir casos como: dict["key"] = value
        node = AssignmentNode(target=p[1], value=p[3])
        p[0] = self._setpos(node, p, 1)  

    def p_nested_id(self, p):
        """nested_id : nested_id DOT ID
                     | ID DOT ID"""
        if len(p) == 4:
            p[0] = AttributeAccessNode(base=p[1], attribute=p[3])

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
        node = AugAssignmentNode(op=p[2], target=p[1], value=p[3])
        p[0] = self._setpos(node, p, 1)

    # ----- CONTROL FLOW -----
    def p_return_stmt(self, p):
        """return_stmt : RETURN expression
                       | RETURN"""
        if len(p) == 3:
            node = ReturnNode(value=p[2])
            p[0] = self._setpos(node, p, 1)
        else:
            node = ReturnNode(value=None)
            p[0] = self._setpos(node, p, 1)

    def p_pass_stmt(self, p):
        """pass_stmt : PASS"""
        p[0] = PassNode()

    def p_break_stmt(self, p):
        """break_stmt : BREAK"""
        p[0] = BreakNode()

    def p_continue_stmt(self, p):
        """continue_stmt : CONTINUE"""
        p[0] = ContinueNode()

    # ----- EXPRESIONES -----
    def p_expression(self, p):
        """expression : or_expression"""
        p[0] = p[1]

    def p_or_expression(self, p):
        """or_expression : or_expression OR and_expression
                         | and_expression"""
        if len(p) == 4:
            node = BinaryOpNode(op="OR", left=p[1], right=p[3])
            p[0] = self._setpos(node, p, 1)
        else:
            p[0] = p[1]

    def p_and_expression(self, p):
        """and_expression : and_expression AND not_expression
                          | not_expression"""
        if len(p) == 4:
            node = BinaryOpNode(op="AND", left=p[1], right=p[3])
            p[0] = self._setpos(node, p, 1)
        else:
            p[0] = p[1]

    def p_not_expression(self, p):
        """not_expression : NOT not_expression
                          | comparison"""
        if len(p) == 3:
            node = UnaryOpNode(op="NOT", operand=p[2])
            p[0] = self._setpos(node, p, 1)
        else:
            p[0] = p[1]

    # ----- COMPARACIONES -----
    def p_comparison(self, p):
        """comparison : arithmetic_expr comp_chain"""
        left = p[1]
        chain = p[2]
        if not chain:
            p[0] = left
        elif len(chain) == 1:
            op, right = chain[0]
            p[0] = ComparisonNode(op=op, left=left, right=right)
        else:
            p[0] = ChainedComparisonNode(left=left, chain=chain)

    def p_comp_chain(self, p):
        """comp_chain : comp_chain comp_op arithmetic_expr
                      | comp_op arithmetic_expr
                      | empty"""
        if len(p) == 2:
            p[0] = []
        elif len(p) == 3:
            p[0] = [(p[1], p[2])]
        else:
            p[0] = p[1] + [(p[2], p[3])]

    def p_comp_op(self, p):
        """comp_op : LESS
                   | GREATER
                   | LESSEQ
                   | GREATEREQ
                   | EQ
                   | NEQ"""
        p[0] = p[1]

    # ----- EXPRESIONES ARITMÉTICAS -----
    def p_arithmetic_expr(self, p):
        """arithmetic_expr : arithmetic_expr PLUS term
                           | arithmetic_expr MINUS term
                           | term"""
        if len(p) == 4:
            p[0] = BinOpNode(op=p[2], left=p[1], right=p[3])
        else:
            p[0] = p[1]

    def p_term(self, p):
        """term : term MULTI factor
                | term DIVIDE factor
                | term FLOORDIV factor
                | term MOD factor
                | factor"""
        if len(p) == 4:
            p[0] = BinOpNode(op=p[2], left=p[1], right=p[3])
        else:
            p[0] = p[1]

    def p_factor(self, p):
        """factor : PLUS factor %prec UPLUS
                  | MINUS factor %prec UMINUS
                  | power"""
        if len(p) == 3:
            p[0] = UnaryOpArithmeticNode(op=p[1], operand=p[2])
        else:
            p[0] = p[1]

    def p_power(self, p):
        """power : primary POW power
                 | primary"""
        if len(p) == 4:
            node = BinaryOpNode(op="POW", left=p[1], right=p[3])
            p[0] = self._setpos(node, p, 1)
        else:
            p[0] = p[1]

    # ----- PRIMARIOS -----
    def p_primary_index(self, p):
        """primary : primary LBRACKET expression RBRACKET"""
        node = IndexAccessNode(base=p[1], index=p[3])
        p[0] = self._setpos(node, p, 1)

    def p_primary_slice(self, p):
        """primary : primary LBRACKET slice_spec RBRACKET"""
        start, end = p[3]
        node = SliceAccessNode(base=p[1], start=start, end=end)
        p[0] = self._setpos(node, p, 1)

    def p_primary_call(self, p):
        """primary : ID LPAREN arg_list_opt RPAREN
                   | nested_id LPAREN arg_list_opt RPAREN
                   | PRINT LPAREN arg_list_opt RPAREN"""
        if p.slice[1].type == "ID":
            callee = IdentifierNode(p[1])
        elif p.slice[1].type == "PRINT":
            callee = IdentifierNode("print")
        else:
            callee = p[1]
        p[0] = CallNode(callee=callee, args=p[3])

    def p_slice_spec(self, p):
        """slice_spec : slice_expr_opt COLON slice_expr_opt"""
        p[0] = (p[1], p[3])

    def p_slice_expr_opt(self, p):
        """slice_expr_opt : expression
        | empty"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = None

    def p_primary_atoms(self, p):
        """primary : nested_id
                   | ID
                   | INTEGER
                   | DECIMAL
                   | SCONST
                   | TRUE
                   | FALSE"""
        tok = p.slice[1].type
        if tok == "nested_id":
            p[0] = p[1]
        elif tok == "ID":
            p[0] = IdentifierNode(p[1])
        elif tok == "INTEGER":
            p[0] = LiteralNode(kind="int", value=p[1])
        elif tok == "DECIMAL":
            p[0] = LiteralNode(kind="float", value=p[1])
        elif tok == "SCONST":
            p[0] = LiteralNode(kind="string", value=p[1])
        elif tok == "TRUE":
            p[0] = LiteralNode(kind="bool", value=True)
        elif tok == "FALSE":
            p[0] = LiteralNode(kind="bool", value=False)

    # ----- TUPLE EXPRESSIONS -----
    def p_tuple_expr(self, p):
        """tuple_expr : or_expression
                      | tuple_expr COMMA or_expression
                      | or_expression COMMA"""
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 3:
            p[0] = TupleNode([p[1]])
        else:
            if isinstance(p[1], TupleNode):
                p[0] = TupleNode(p[1].elements + [p[3]])
            else:
                p[0] = TupleNode([p[1], p[3]])

    def p_primary_tuple_or_group(self, p):
        """primary : LPAREN expr_list_plain RPAREN"""
        if len(p[2]) > 1:
            p[0] = TupleNode(p[2])
        else:
            p[0] = GroupNode(p[2][0])

    def p_primary_tuple_trailing(self, p):
        """primary : LPAREN expr_list_plain COMMA RPAREN"""
        p[0] = TupleNode(p[2])

    # ----- LISTAS Y DICCIONARIOS -----
    def p_primary_list(self, p):
        """primary : LBRACKET expr_list_plain_opt RBRACKET
                   | LBRACKET expr_list_plain COMMA RBRACKET"""
        p[0] = ListNode(p[2])

    def p_primary_dict_or_set(self, p):
        """primary : LKEY key_value_list_opt RKEY
        | LKEY key_value_list COMMA RKEY
        | LKEY expr_list_plain_opt RKEY
        | LKEY expr_list_plain COMMA RKEY"""
        # Distinguir entre dict y set
        # Si p[2] es una lista de pares (key, value), es dict
        # Si p[2] es una lista de expresiones simples, es set
        if len(p[2]) == 0:
            # {} vacío es dict por defecto en Python
            p[0] = DictNode([])
        elif isinstance(p[2], list) and len(p[2]) > 0:
            # Verificar si el primer elemento es una tupla (par key-value)
            if isinstance(p[2][0], tuple) and len(p[2][0]) == 2:
                p[0] = DictNode(p[2])
            else:
                p[0] = SetNode(p[2])
        else:
            p[0] = DictNode([])

    # ----- UTILIDADES PARA LISTAS/ARGUMENTOS -----
    def p_arg_list(self, p):
        """arg_list : arg_list COMMA arg
                    | arg"""
        p[0] = p[1] + [p[3]] if len(p) == 4 else [p[1]]

    def p_arg(self, p):
        """arg : expression
               | ID ASSIGN expression
               | nested_id ASSIGN expression"""
        if len(p) == 2:
            p[0] = ArgumentNode(value=p[1])
        else:
            key = IdentifierNode(p[1]) if isinstance(p[1], str) else p[1]
            p[0] = ArgumentNode(value=p[3], keyword=key)

    def p_arg_list_opt(self, p):
        """arg_list_opt : arg_list
                        | empty"""
        p[0] = p[1] if p[1] is not None else []

    def p_expr_list_plain(self, p):
        """expr_list_plain : expression
                           | expr_list_plain COMMA expression"""
        p[0] = p[1] + [p[3]] if len(p) == 4 else [p[1]]

    def p_expr_list_plain_opt(self, p):
        """expr_list_plain_opt : expr_list_plain
                               | empty"""
        p[0] = p[1] if p[1] is not None else []

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

    def p_empty(self, p):
        """empty :"""
        pass

    # ----- ERROR HANDLING -----
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


# ----- HELPER FUNCTIONS -----
def _line_info_from_lexpos(text: str, lexpos: int):
    """Return (line_text, col0, col1) given a 0-based lexpos."""
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
        return str(e)


def run_single_file(path: str):
    """Parse one file with a fresh Parser; return a rich dict for reporting."""
    errors: list[Error] = []
    parser = Parser(errors, debug=False)

    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

    parser.lexer.data = code
    result = None
    uncaught = None
    
    try:
        parser.lexer.lex.lineno = 1
        result = parser.parser.parse(code, lexer=parser.lexer.lex, debug=False)

        if result is not None and parser._has_lexer_errors():
            parser._validate_ast_for_empty_string_literals(result)

    except Exception as ex:
        uncaught = str(ex)

    has_lex_err = parser._has_lexer_errors()
    has_par_err = parser._has_parser_errors()
    success = (result is not None) and (uncaught is None) and (len(errors) == 0)

    return {
        "path": path,
        "success": success,
        "result": result.to_tuple() if (success and result) else None,
        "ast_object": result,  # Keep the actual AST object
        "error_count": len(errors),
        "has_lexer_errors": has_lex_err,
        "has_parser_errors": has_par_err,
        "uncaught": uncaught,
        "errors_raw": [str(e) for e in errors],
    }


# --- MAIN TEST ---
if __name__ == "__main__":
    test_files = [
        "tests/parser_ERR_dict_trailing_comma.py",
        "tests/parser_ERR_inline_function.py",
        "tests/parser_ERR_list_trailing_comma.py",
        "tests/parser_ERR_missing_colon_or_indent.py",
        "tests/parser_ERR_params_and_calls.py",
        "tests/parser_ERR_semicolons.py",

        "tests/parser_OK_assign_expr.py",
        "tests/parser_OK_augmented_assigns.py",
        "tests/parser_OK_chained_comparison.py",
        "tests/parser_OK_class_and_method.py",
        "tests/parser_OK_dict_trailing_comma.py",
        "tests/parser_OK_function_control.py",
        "tests/parser_OK_inline_function.py",
        "tests/parser_OK_keyword_args.py",
        "tests/parser_OK_list_trailing_comma.py",
        "tests/parser_OK_minimal.py",
        "tests/parser_OK_params_and_calls.py",
        "tests/parser_OK_print_try.py",
        "tests/parser_OK_top_level_if.py",
        "tests/parser_OK_tuple_unpacking.py",
        "transpiler_tests/teacher_test.py",
    ]

    # Run all tests
    reports = []
    for path in test_files:
        rep = run_single_file(path)
        reports.append(rep)

    # --- Write human-readable report ---
    with open("Parser_report.txt", "w", encoding="utf-8") as out:
        for rep in reports:
            out.write(f"=== {rep['path']} ===\n")
            status = "OK" if rep["success"] else "ERROR"
            out.write(f"Status: {status}\n")
            if rep["uncaught"]:
                out.write(f"Uncaught exception: {rep['uncaught']}\n")
            out.write(f"Lexer errors: {rep['has_lexer_errors']} | Parser errors: {rep['has_parser_errors']}\n")
            out.write(f"Total errors: {rep['error_count']}\n")
            
            if rep["success"] and rep["ast_object"]:
                out.write("\n--- AST (printAST format) ---\n")
                out.write(rep["ast_object"].printAST())
                out.write("\n")
            else:
                for line in rep["errors_raw"]:
                    out.write(line + "\n")
            out.write("\n")

    # --- Write machine-readable JSON logs ---
    # Note: We need to convert AST objects to tuples for JSON serialization
    json_reports = []
    for rep in reports:
        json_rep = {
            "path": rep["path"],
            "success": rep["success"],
            "result": rep["result"],  # Already converted to tuple
            "error_count": rep["error_count"],
            "has_lexer_errors": rep["has_lexer_errors"],
            "has_parser_errors": rep["has_parser_errors"],
            "uncaught": rep["uncaught"],
            "errors_raw": rep["errors_raw"]
        }
        json_reports.append(json_rep)

    with open("logs.json", "w", encoding="utf-8") as jf:
        json.dump(json_reports, jf, indent=2, ensure_ascii=False)

    # --- Terminal summary ---
    print("\n" + "="*60)
    print("PARSER TEST SUMMARY")
    print("="*60)
    for rep in reports:
        status = "[OK]" if rep["success"] else "[FAIL]"
        print(f"{status:8}  {rep['error_count']:2} errors  {rep['path']}")

    # Count successes
    total = len(reports)
    passed = sum(1 for r in reports if r["success"])
    print("="*60)
    print(f"TOTAL: {passed}/{total} tests passed")
    print("="*60)
