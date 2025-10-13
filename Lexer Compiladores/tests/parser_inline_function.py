# Inline body 
def f(): return 0
def g(x): x + 1
def h(a, b):
    return a + b
class C:
    def m(self): return 42

# Should fail:
def f(): a = 1; b = 2      # semicolons unsupported in this grammar
def bad(): if x: y         # control-flow can’t be inline
def nope(): 
    return 0
    # and then indent here → your lexer will raise "Unexpected indentation after one-line suite"

