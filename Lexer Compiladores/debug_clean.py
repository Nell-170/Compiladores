import sys
sys.path.insert(0, '.')

from Transpiler import Transpiler
from ParserAST import Parser
from utils import Error

# Leer el archivo
with open('transpiler_tests/teacher_test.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Crear transpilador y procesar
transpiler = Transpiler()

# Detectar si hay cronómetro
transpiler.use_timer = "import time" in code and "inicio = time.time()" in code

# Limpiar código si tiene cronómetro
if transpiler.use_timer:
    code = transpiler._remove_timer_lines(code)

print("=== Código Python después de limpiar timers ===")
print(code)
print("\n=== Búsqueda de 'a[4]' ===")
if 'a[4]' in code:
    idx = code.find('a[4]')
    print(f"Encontrado en posición {idx}")
    print(code[max(0, idx-50):idx+50])
else:
    print("NO ENCONTRADO")
