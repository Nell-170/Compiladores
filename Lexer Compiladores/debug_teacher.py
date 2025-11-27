import sys
sys.path.insert(0, '.')

from Transpiler import Transpiler

try:
    transpiler = Transpiler()
    print("Transpilando teacher_test.py...")
    resultado = transpiler.transpile_file('transpiler_tests/teacher_test.py')
    print("OK: Transpilacion exitosa")
    with open('output_teacher.cpp', 'w', encoding='utf-8') as f:
        f.write(resultado)
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
