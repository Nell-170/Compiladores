# Tests sobre parámetros y llamadas (varios casos concatenados)

# 1) params_simple.py — Aceptado sintácticamente
def f(a, b, c):
    pass

# 2) params_self.py — Aceptado sintácticamente (método con self)
class C:
    def m(self, x):
        pass

# 3) params_self_attr.py — Aceptado sintácticamente -> semántica debería rechazar
class C2:
    def m(self, self.x):
        pass

# 4) nested_param_complex.py — Aceptado sintácticamente -> semántica debería rechazar obj.attr
def g(a, obj.attr, z):
    pass

# 5) param_default_syntax.py — Sintácticamente inválido con la gramática actual (ID=expr en params)
def h(x=1, y=2): # ERROR
    pass

# 6) class_inherit_nested.py — Herencia con nested_id en params_list (aceptado sintácticamente)
class D(B.C):
    pass

# 7) call_keyword_args.py — Llamada con keyword arg
print(msg="hello")

# 8) call_mixed_args.py — Posicional + keyword (aceptado sintácticamente)
print("hi", msg="hello")

# 9) call_pos_after_kw.py — Posicional después de keyword (debería fallar en semántica)
print(msg="hello", "oops")

# 10) invalid_func_missing_colon.py — Error sintáctico (falta coma entre params)
def bad(a b): # ERROR
    pass