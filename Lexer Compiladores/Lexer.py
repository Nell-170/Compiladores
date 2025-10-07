import ply.lex as lex
import sys
import ast

from utils import Error
from symbol_table import SymbolTable


class Lexer:
    def __init__(self, errors: list[Error], debug=False):
        self.lex = None
        self.saw_token_on_line = False
        self.data = None
        self.debug = debug
        self.symbol_table = SymbolTable()
        self.reserved_map = {}
        self.errors = errors  # use the same error list as the parser
        for r in self.reserved:
            # map keyword text in lowercase to its token name in uppercase
            if r in ("TRUE", "FALSE"):
                self.reserved_map[r.capitalize()] = r  # "True" y "False"
            else:
                self.reserved_map[r.lower()] = r

    reserved = (
        # TODO(any): add PRINT token and rule
        # TODO(any): add TRY CATCH token and rule
        # Control flow
        "IF", "ELSE", "ELIF", "WHILE", "FOR", "IN", 
        "BREAK", "CONTINUE", "PASS",
        # Definitions
        "DEF", "RETURN", "CLASS",
        # Boolean types
        "TRUE", "FALSE",
        # Logical operators
        "AND", "OR", "NOT",
        # Synthetic indentation and newline
        "INDENT", "DEDENT", "NEWLINE",
    )

    tokens = reserved + (
        # Literals
        "ID",
        "INTEGER",
        "DECIMAL",
        "SCONST",
        # Operators
        "PLUS",
        "MINUS",
        "MULTI",
        "DIVIDE",
        "MOD",
        "POW",
        "FLOORDIV",
        # Relational operators
        "EQ",
        "NEQ",
        "LESS",
        "GREATER",
        "LESSEQ",
        "GREATEREQ",
        # Shifts
        "DOUBLEGREATER",
        "DOUBLELESS",
        # Triple shifts
        "TRIPLELESS",
        "TRIPLEGREATER",
        "LESSGREATER",
        # Assignment
        "ASSIGN",
        "PLUS_ASSIGN",
        "MINUS_ASSIGN",
        "MULTI_ASSIGN",
        "DIVIDE_ASSIGN",
        "MOD_ASSIGN",
        "FLOORDIV_ASSIGN",
        "POW_ASSIGN",
        "ASSIGN_COLON",
        "TERNAL",
        # Delimiters
        "LPAREN",
        "RPAREN",
        "LBRACKET",
        "RBRACKET",
        "LKEY",
        "RKEY",
        "COMMA",
        "SEMICOLON",
        "COLON",
        "DOT",
    )

    # Tab expansion to compute indentation column
    def _tab_expand_col(self, s, tabstop=8):
        col = 0
        for ch in s:
            if ch == "\t":
                col = (col // tabstop + 1) * tabstop
            else:
                col += 1
        return col

    # Build synthetic tokens (NEWLINE/INDENT/DEDENT)
    def _emit(self, toktype, value=None, lineno=None, lexpos=None):
        t = lex.LexToken()
        t.type = toktype
        t.value = value if value is not None else toktype
        t.lineno = lineno if lineno is not None else self.lex.lineno
        t.lexpos = lexpos if lexpos is not None else self.lex.lexpos
        return t

    # Simple regex rules

    # Operators
    t_PLUS = r"\+"
    t_MINUS = r"-"
    t_MULTI = r"\*"
    t_DIVIDE = r"/"
    t_MOD = r"%"
    t_POW = r"\*\*"
    t_FLOORDIV = r"//"

    # Relational operators
    t_EQ = r"=="
    t_NEQ = r"!="
    t_LESS = r"<"
    t_GREATER = r">"
    t_LESSEQ = r"<="
    t_GREATEREQ = r">="

    # Shifts
    t_DOUBLEGREATER = r">>"
    t_DOUBLELESS = r"<<"

    # Triple shifts
    t_TRIPLEGREATER = r">>>"
    t_TRIPLELESS = r"<<<"

    t_LESSGREATER = r"<>"  # not equal (SQL style)

    # Assignment
    t_ASSIGN = r"="
    t_PLUS_ASSIGN = r"\+="
    t_MINUS_ASSIGN = r"-="
    t_MULTI_ASSIGN = r"\*="
    t_DIVIDE_ASSIGN = r"/="
    t_MOD_ASSIGN = r"%="
    t_FLOORDIV_ASSIGN = r"//="
    t_POW_ASSIGN = r"\*\*="

    t_ASSIGN_COLON = r":="
    t_TERNAL = r"\?"

    # Delimiters
    t_COMMA = r","
    
    # Semicolon is not allowed as a line separator in our Python version
    def t_SEMICOLON(self, t):
        r";"
        # Record error and skip token
        self.errors.append(
            Error(
                "The semicolon (;) is not allowed as a line separator in our Fangless Python.",
                t.lineno,
                t.lexpos,
                "lexer",
                self.data,
            )
        )
        # swallow it so the parser can't use it as a separator
        pass
        
    t_COLON = r":"
    t_DOT = r"\."

    # String literals: "..." or '...' (no newlines)
    def t_DQSTRING(self, t):
        r'"([^"\\\n]|\\.)*"'
        raw = t.value               # entire matched lexeme with quotes
        t.raw = raw                 # keep original, useful for error messages

        try:
            # Evaluate like Python
            t.value = ast.literal_eval(raw)
        except Exception as exc:
            # If you want to error on bad escapes:
            self.errors.append(
                Error(f"Invalid string literal: {exc}", t.lineno, t.lexpos, "lexer", self.data)
            )
            # Fallback: strip quotes without unescaping so parser can continue
            t.value = raw[1:-1]
            
        t.type = 'SCONST'
        return t

    def t_SQSTRING(self, t):
        r"'([^'\\\n]|\\.)*'"
        raw = t.value               # entire matched lexeme with quotes
        t.raw = raw                 # keep original, useful for error messages

        try:
            # Evaluate like Python
            t.value = ast.literal_eval(raw)
        except Exception as exc:
            # If you want to error on bad escapes:
            self.errors.append(
                Error(f"Invalid string literal: {exc}", t.lineno, t.lexpos, "lexer", self.data)
            )
            # Fallback: strip quotes without unescaping so parser can continue
            t.value = raw[1:-1]
            
        t.type = 'SCONST'
        return t

    # Ignore spaces and tabs outside indentation measurement
    t_ignore = " \t"

    # Delimiters with paren-level tracking for implicit continuation
    def t_LPAREN(self, t):
        r"\("
        self.paren_level += 1
        t.type = "LPAREN"
        return t

    def t_LBRACKET(self, t):
        r"\["
        self.paren_level += 1
        t.type = "LBRACKET"
        return t

    def t_LKEY(self, t):
        r"\{"
        self.paren_level += 1
        t.type = "LKEY"
        return t

    def t_RPAREN(self, t):
        r"\)"
        self.paren_level = max(0, self.paren_level - 1)
        t.type = "RPAREN"
        return t

    def t_RBRACKET(self, t):
        r"\]"
        self.paren_level = max(0, self.paren_level - 1)
        t.type = "RBRACKET"
        return t

    def t_RKEY(self, t):
        r"\}"
        self.paren_level = max(0, self.paren_level - 1)
        t.type = "RKEY"
        return t

    # Explicit line continuation with backslash
    def t_backslash_cont(self, t):
        r"\\\n"
        t.lexer.lineno += 1
        self.backslash_cont = True
        # suppress the following logical NEWLINE
        pass

    def t_newline(self, t):
        r'\n[ \t]*'
        t.lexer.lineno += 1
        
        # Skip indentation for continuation lines
        if self.paren_level > 0 or self.backslash_cont:
            self.backslash_cont = False
            return
        
        # Extract indentation text after newline
        indent_text = t.value[1:]
        # Calculate current indentation level
        current_col = self._tab_expand_col(indent_text)
        
        # Check if next line is empty or comment
        nxt = self.lex.lexdata[self.lex.lexpos:self.lex.lexpos+1]
        if nxt in ('', '\n', '#'):
            # Don't emit NEWLINE/INDENT/DEDENT for empty lines or comments
            return

        # Enforce “multiples of INDENT_STEP”
        if current_col > 0 and current_col % self.INDENT_STEP != 0:
            self.errors.append(
                Error(
                    f"Indentation must be a multiple of {self.INDENT_STEP} spaces",
                    t.lexer.lineno,
                    t.lexpos,
                    "lexer",
                    self.data,
                )
            )
        
        # Always emit NEWLINE for lines with real content
        t.type = 'NEWLINE'
        t.value = 'NEWLINE'
        
        # Get current indentation level from stack
        prev_col = self.indent_stack[-1]

        # Case A: last colon required an indented block
        if self.expect_indent and current_col <= prev_col:
            self.errors.append(
                Error(
                    "Expected an indented block",
                    t.lexer.lineno,
                    t.lexpos,
                    "lexer",
                    self.data,
                )
            )
            self.expect_indent = False  # reset even on error
        elif self.expect_indent and current_col > prev_col:
            # If we did get the expected indent, clear the flag
            self.expect_indent = False

        # Case B: last colon had an inline suite → forbid indent on next line
        if self.forbid_indent_next and current_col > prev_col:
            self.errors.append(
                Error(
                    "Unexpected indentation after one-line suite",
                    t.lexer.lineno,
                    t.lexpos,
                    "lexer",
                    self.data,
                )
            )
        # Either way, clear the guard after we’ve examined this newline
        self.forbid_indent_next = False
        
        # Emit INDENT/DEDENT tokens
        # Compare current vs previous indentation
        if current_col > prev_col:
            # INDENT case - indent increased
            self.indent_stack.append(current_col)
            self.pending.append(self._emit('INDENT'))
        elif current_col < prev_col:
            # DEDENT case(s) - indent decreased
            # Emit enough DEDENTs to reach current level
            while self.indent_stack and self.indent_stack[-1] > current_col:
                self.indent_stack.pop()
                self.pending.append(self._emit('DEDENT'))
            
            # Verify indentation matches a previous level
            if self.indent_stack[-1] != current_col:
                self.errors.append(
                    Error(
                        "Inconsistent dedent",
                        t.lexer.lineno,
                        t.lexpos,
                        "lexer",
                        self.data,
                    )
                )
        
        # Reset flag after processing this newline
        self.saw_token_on_line = False
        
        # return the NEWLINE token
        return t

    # Identifiers and reserved words
    def t_ID(self, t):
        r"""[a-zA-Z_][a-zA-Z0-9_]*"""
        self.saw_token_on_line = True
        if self.debug:
            print(f"DEBUG(LEXER): {t.value} on line {t.lineno}, position {t.lexpos}")
        # lookup in lowercase so 'True' -> 'TRUE', 'In' -> 'IN', etc.
        t.type = self.reserved_map.get(t.value, "ID")
        return t

    # Numbers: decimal must be matched before integer
    def t_DECIMAL(self, t):
        r"""\d+\.\d+"""
        t.value = float(t.value)
        return t

    def t_INTEGER(self, t):
        r"""\d+"""
        t.value = int(t.value)
        return t

    # Comments: ignore
    def t_COMMENT(self, t):
        r"""\#.*"""
        pass

    # Lexical errors
    def t_error(self, t):
        self.errors.append(
            Error(
                "Illegal character '%s'" % t.value[0],
                t.lineno,
                t.lexpos,
                "lexer",
                self.data,
            )
        )
        print(self.errors[-1])
        t.lexer.skip(1)

    # Hook: return synthetic tokens first
    def hooked_token(self):
        # First deliver any pending indentation tokens
        if self.pending: 
            return self.pending.pop(0)
            
        # Then get next token from lexer
        tok = self.orig_token()
        
        # If we have a real token, mark that we've seen content
        if tok and tok.type not in ('NEWLINE', 'INDENT', 'DEDENT'):
            self.saw_token_on_line = True

            # Decide indent expectation when we see a COLON outside parentheses
            if tok.type == 'COLON' and self.paren_level == 0:
                # Peek ahead to the end of the physical line
                data = self.lex.lexdata
                i = self.lex.lexpos
                # skip horizontal whitespace
                while i < len(data) and data[i] in ' \t':
                    i += 1
                if i < len(data):
                    next_char = data[i]
                    if next_char == '\n' or next_char == '#':
                        # Nothing else on this line → block required next line
                        self.expect_indent = True
                        self.forbid_indent_next = False
                    else:
                        # Inline suite (e.g., "if x: y") → next line must NOT indent
                        self.forbid_indent_next = True
                        self.expect_indent = False

        # If end of input and still indented, unwind all remaining indentation
        if tok is None and len(self.indent_stack) > 1:
            # Pop all remaining indentation levels and emit DEDENTs
            while len(self.indent_stack) > 1:
                self.indent_stack.pop()
                self.pending.append(self._emit('DEDENT'))
            return self.pending.pop(0) if self.pending else None
            
        return tok

    def build(self):
        self.lex = lex.lex(module=self)
        # Save original method and wrap
        self.orig_token = self.lex.token
        self.lex.token = self.hooked_token

        # Indentation tracking structures
        self.indent_stack = [0]  # indentation levels
        self.pending = []  # synthetic tokens queue
        self.paren_level = 0  # inside (), [], {}
        self.backslash_cont = False
        self.INDENT_STEP = 4  # multiples of 4
        # Track whether any non-NEWLINE/INDENT/DEDENT token was seen on the current line
        self.saw_token_on_line = False
        # Track if we're expecting an indentation after a colon
        self.expect_indent = False
        # Track if we just saw an inline suite and need to forbid indentation
        self.forbid_indent_next = False
        self.prev_token = None
        self.defFlag = False


def lexer_tester(path, lexer_instance):
    # Save original stdout
    stdout_original = sys.stdout

    with open(path, "r", encoding="utf-8") as f:
        with open("Lexer_report.txt", "w", encoding="utf-8") as lexerReport:
            sys.stdout = lexerReport  # redirect stdout to the file

            lexer_instance.build()
            lexer_instance.data = f.read()
            lexer_instance.lex.input(lexer_instance.data)

            while True:
                tok = lexer_instance.lex.token()
                if not tok:
                    break
                print(tok)

    # Restore stdout
    sys.stdout = stdout_original

def pretty_print_errors(errors):
    if not errors:
        print("\nDetected errors: none.")
        return
    print(f"\nDetected {len(errors)} errors:")
    for i, e in enumerate(errors, 1):
        # each error on its own block with a leading blank line
        print(f"\n[{i}] {e}") 


# --- MAIN TEST ---
if __name__ == "__main__":
    # TEST
    errors = []
    lexer = Lexer(errors, debug=False)

    # File to test
    path = "lexer_test.py"
    lexer_tester(path, lexer)
    pretty_print_errors(errors)

