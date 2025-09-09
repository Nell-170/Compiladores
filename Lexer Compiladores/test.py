# -*- coding: utf-8 -*-
# Lexer stress test — contains intentional errors to exercise indentation & newline logic.

# --- 1) Valid block to warm up ---
def random_operation(a, b):
    c = a + b
    # Hi I'm a comment!
    return c + a * b + 2.6548


# --- 2) Semicolon forbidden anywhere ---
def f():
    x = 0; return 0          # EXPECT: semicolon forbidden


# --- 3) Inline suite followed by an indented next line (should NOT indent) ---
def g(): return 1
    return 2                 # EXPECT: Unexpected indentation after one-line suite


# --- 4) Colon + NEWLINE requires an indented block next line ---
if True:
x = 1                        # EXPECT: Expected an indented block


# --- 5) Indentation must be multiple of 4 (3 spaces here) ---
if 1:
   bad = 3                   # EXPECT: Indentation must be a multiple of 4
# back to base


# --- 6) Inconsistent dedent (dedent to a level never used: 6 spaces) ---
if True:
    if True:
        deep = 42
      oops = deep            # (6 spaces) EXPECT: Inconsistent dedent
# back to base


# --- 7) Another inline suite + semicolon chain ---
if 5 > 8: a = 9; b = 10      # EXPECT: semicolon forbidden


# --- 8) Explicit line continuation with backslash (should NOT emit NEWLINE/INDENT) ---
def linesum():
    total = 1 + \
            2 + \
            3
    return total


# --- 9) Paren/bracket continuation (inner indents are ignored by lexer) ---
nums = [
    1,
    2,  # comment after item
    3,
]


# --- 10) Base-level RETURN (lexer should allow; parser would complain later) ---
return 0                     # NOTE: lexer should NOT treat this as an indent error


# --- 11) Strings with escapes and # inside (shouldn’t start a comment) ---
s1 = "hash # inside ok"
s2 = 'quote \" escape ok'


# --- 12) Illegal character to trigger t_error ---
weird = 1 § 2                # EXPECT: Illegal character '§'


# --- 13) Mixed: colon then comment on same line → block required next line ---
if True:  # comment after colon
print("no indent")           # EXPECT: Expected an indented block


# --- 14) Valid inline suites that should pass ---
def ok_inline(): return 7
if 6 < 9: y = 7


# --- 15) EOF with pending dedents (lexer should auto-emit DEDENTs at EOF) ---
def outer():
    def inner():
        x = 1
        if x:
            y = 2
            z = 3
# EOF here; no explicit dedent lines

def func(): 5 < 2
return 0

x = 1
def func() : 1+1
if x > 5:
    a = 0
