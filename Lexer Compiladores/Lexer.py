import ply.lex as lex
import sys

from utils import Error
from symbol_table import SymbolTable


class Lexer:
    def __init__(self, errors: list[Error], debug=False):
        self.lex = None
        self.data = None
        self.debug = debug
        self.symbol_table = SymbolTable()
        self.reserved_map = {}
        self.errors = errors  # to use the same list of errors that the parser uses
        for r in self.reserved:
            self.reserved_map[r.lower()] = r

    reserved = (
        # Control de flujo
        'IF', 'ELSE', 'ELIF', 'WHILE', 'FOR', 'BREAK', 'CONTINUE', 'PASS', 
        # Definiciones
        'DEF', 'RETURN', 'CLASS', 
        # Tipos booleanos
        'TRUE', 'FALSE',
        # Operadores lógicos
        'AND', 'OR', 'NOT',
    )

    tokens = reserved + (
        # Literals
        'ID', 'NUMBER', 'SCONST', # Qué es SCONST?

        # Operators
        'PLUS', 'MINUS', 'MULTI', 'DIVIDE', 'MOD', 'POW', 'FLOORDIV',
        
        'EQ', 'NEQ', 'LESS', 'GREATER', 'LESSEQ', 'GREATEREQ',
        'DOUBLEGREATER', 'DOUBLELESS', 'TRIPLELESS', 'TRIPLEGREATER', 
        'LESSGREATER', 

        # Assignment operators
        'ASSIGN','PLUS_ASSIGN', 'MINUS_ASSIGN', 'MULTI_ASSIGN', 'DIVIDE_ASSIGN', 'MOD_ASSIGN', 'FLOORDIV_ASSIGN', 'POW_ASSIGN',
        'ASSIGN_COLON', 'TERNAL',

        # Delimitation symbols
        'LPAREN', 'RPAREN', 'LBRACKET', 'RBRACKET', 'LBRACE', 'RBRACE',
        'COMMA', 'SEMICOLON', 'COLON', 'DOT',

        'COMMENT',
    )

    # Index structures
    # last seen indent widths; should be multiples of 4; 0 means no indent
    indent_stack = [0]
    # queue of tokens we've created 
    pending = []
    # need to keep track of if we're inside a (), [], {} ; if not, then we suppress INDENT/DEDENT
    paren_level = 0
    # if newline was suppressed
    backslash_cont = False

    # Index helpers
    INDENT_STEP = 4

    # Traces how many '\s' are in a leading whitespace
    # tabstop defaults to 8 per UNIX convention 
    def _tab_expand_col(str, tabstop = 8):
        col = 0
        for chr in str:
            # Deal with tabs
            if chr == '\t':
                # Jumps to the next multiple of tabstop
                col = (col // tabstop + 1) * tabstop
            # Deal with spaces
            else:
                col += 1
        return col

    # Need to manufacture tokens since these are separate from reserved keywords
    # Since its context-sensitive
    def _emit(toktype, value = None, lineno = None, lexpos = None):
        t = lex.LexToken()      # make an empty PLY token
        # token name the grammar uses. must match something in tokens = (...)
        t.type = toktype

        # payload for the token
        # useful for data tokens (STRING, NUMBER...)
        t.value = value if value is not None else toktype

        # line number the token belongs to
        t.lineno = lineno if lineno is not None else lexer.lineno

        # character offset in the input string (defaults to current position of scanner)
        # useful for error finding
        t.lexpos = lexpos if lexpos is not None else lexer.lexpos
        return t

    # Regular expression rules for simple tokens

    # Operators
    # Single-character operators
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_MULTI = r'\*'
    t_DIVIDE = r'/'
    t_MOD = r'%'
    t_POW = r'\*\*'
    t_FLOORDIV = r'//'

    # Relation operators
    t_EQ = r'=='
    t_NEQ = r'!='
    t_LESS = r'<'
    t_GREATER = r'>'
    t_LESSEQ = r'<='
    t_GREATEREQ = r'>='
    
    # Double-character operators
    t_DOUBLEGREATER = r'>>'
    t_DOUBLELESS = r'<<'
    
    # Triple-character operators
    t_TRIPLEGREATER = r'>>>'
    t_TRIPLELESS = r'<<<'
    
    t_LESSGREATER = r'<>'

    # Assignment operators
    t_ASSIGN = r'='
    t_PLUS_ASSIGN = r'\+='
    t_MINUS_ASSIGN = r'-='
    t_MULTI_ASSIGN = r'\*='
    t_DIVIDE_ASSIGN = r'/='
    t_MOD_ASSIGN = r'%='
    t_FLOORDIV_ASSIGN = r'//='
    t_POW_ASSIGN = r'\*\*='

    t_ASSIGN_COLON = r':='
    t_TERNAL = r'\?'

    # Delimitation symbol
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_COMMA = r','
    t_SEMICOLON = r';'
    t_COLON = r':'
    t_DOT = r'\.'



    # String literal (to identify strings inside double quotes "..." | '...')
    t_SCONST = r'(["\'])([^\\\n]|(\\.))*?(["\'])'

    # Skip spaces and tabs outside of a new line calculation
    t_ignore = ' \t'

    # Identifiers (names of variables, functions, and classes) and reserved words
    def t_ID(self, t):
        r"""[a-zA-Z][a-zA-Z0-9_]*"""
        if self.debug:
            print(f'DEBUG(LEXER): {t.value.upper()} on line {t.lineno}, position {t.lexpos}')
        t.type = self.reserved_map.get(t.value, 'ID')
        return t

    # Number literal (integer and decimal)
    def t_NUMBER(self, t):
        r"""\d+"""
        t.value = int(t.value)
        return t

    def t_DECIMAL(self, t):
        r"""\d+\.\d+"""
        t.value = float(t.value)
        return t 

    def t_COMMENT(self, t):
        r"""\#.*"""
        pass

    def t_LITERAL(self, t):
        r"""\"[^"]*\\"""
        return t

    def t_NEWLINE(self, t):
        r"""\n+"""
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        self.errors.append(Error("Illegal character '%s'" % t.value[0], t.lineno, t.lexpos, 'lexer', self.data))
        print(self.errors[-1])
        t.lexer.skip(1)

    def build(self, ):
        self.lex = lex.lex(module=self)


def lexer_tester(path, lexer_instance):
    # Guardamos stdout original
    stdout_original = sys.stdout

    # Abrimos el archivo fuente
    with open(path, 'r', encoding='utf-8') as f:
        # Abrimos archivo de reporte
        with open("Lexer_report.txt", "w", encoding="utf-8") as archivoLexer:
            sys.stdout = archivoLexer  # redirigimos stdout al archivo

            lexer_instance.build()  # construimos el lexer de PLY
            lexer_instance.data = f.read()
            lexer_instance.lex.input(lexer_instance.data)

            # Iteramos sobre los tokens
            while True:
                tok = lexer_instance.lex.token()
                if not tok:
                    break
                print(tok)

    # Restauramos stdout
    sys.stdout = stdout_original


# PRUEBA 

errors = []
lexer = Lexer(errors, debug=True)

# Archivo que quieras probar
path = "test.py"
lexer_tester(path, lexer)

print("Errores detectados:", errors)
