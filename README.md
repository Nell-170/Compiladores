# Transpilador de Python a C++

Este proyecto implementa un transpilador educativo para un subconjunto de Python. El flujo procesa el código fuente mediante análisis léxico y sintáctico, construye un árbol de sintaxis abstracta (AST) y genera código C++ recorriendo ese árbol con el patrón **Visitor**.

> No es una implementación completa de Python: el lenguaje aceptado y las construcciones que pueden generarse están limitados por la gramática y los visitantes implementados.

## Flujo del transpilador

1. **Análisis léxico:** [`Lexer Compiladores/Lexer.py`](Lexer%20Compiladores/Lexer.py) usa PLY para reconocer tokens, palabras reservadas y operadores. También maneja la indentación y los saltos de línea, y registra errores léxicos.
2. **Análisis sintáctico:** [`Lexer Compiladores/ParserAST.py`](Lexer%20Compiladores/ParserAST.py) define la gramática con PLY Yacc y construye nodos para representar el programa.
3. **Árbol de sintaxis abstracta:** [`Lexer Compiladores/ast_nodes.py`](Lexer%20Compiladores/ast_nodes.py) contiene los nodos del AST. Su método `accept(visitor)` despacha cada nodo al método `visit_<TipoDeNodo>` correspondiente.
4. **Transpilación:** [`Lexer Compiladores/Transpiler.py`](Lexer%20Compiladores/Transpiler.py) implementa esos visitantes y genera C++. El código generado usa [`Lexer Compiladores/PyObject.hpp`](Lexer%20Compiladores/PyObject.hpp) como soporte para representar valores.

La gramática contempla, entre otras construcciones, definiciones de funciones y clases, asignaciones, expresiones, llamadas, condicionales, ciclos y estructuras como listas, tuplas, diccionarios y conjuntos. La disponibilidad de cada construcción en el código C++ generado depende de que tenga su visitante de transpilación implementado.

## Requisitos

- Python 3
- PLY 3.11 (se instala desde `requirements.txt`)
- Para compilar o ejecutar el C++ generado: `g++` o `clang++`

## Instalación

Desde la raíz del repositorio:

```sh
cd "Lexer Compiladores"
python -m pip install -r requirements.txt
```

## Uso

Desde la carpeta `Lexer Compiladores`, ejecuta:

```sh
python Transpiler.py
```

El programa solicita un modo:

| Modo | Acción |
|---|---|
| `1` | Transpila el archivo de entrada y guarda el resultado en `output.cpp`. |
| `2` | Transpila y compila el resultado con `g++` o `clang++` usando C++17. |
| `3` | Transpila, compila y ejecuta el programa generado. |

El ejemplo configurado en el punto de entrada es `transpiler_tests/list_test.py`. Para procesar otro archivo, cambia la variable `file_path` al final de `Transpiler.py`. Los modos 2 y 3 requieren que el compilador elegido esté disponible en el sistema.

## Pruebas y herramientas auxiliares

Desde `Lexer Compiladores`:

- `python Lexer.py` ejecuta la prueba del lexer definida en `tests/lexer_test.py` y genera `Lexer_report.txt`.
- `python ParserAST.py` ejecuta los casos de análisis sintáctico de `tests/` y genera `Parser_report.txt` y `logs.json`.
- `transpiler_tests/` contiene programas de ejemplo para probar la transpilación.

## Estructura del proyecto

- [`Lexer Compiladores/`](Lexer%20Compiladores/): implementación del lexer, parser, AST y transpilador.
- [`Lexer Compiladores/tests/`](Lexer%20Compiladores/tests/): casos de prueba para el lexer y el parser.
- [`Lexer Compiladores/transpiler_tests/`](Lexer%20Compiladores/transpiler_tests/): ejemplos para la transpilación.
- [`Lexer Compiladores/symbol_table.py`](Lexer%20Compiladores/symbol_table.py): tabla de símbolos usada por el lexer.
- [`Lexer Compiladores/utils.py`](Lexer%20Compiladores/utils.py): utilidades y estructura para reportar errores.

## Créditos

- B88948 — Antonio Emmanuel González Sandoval
- C17546 — Milton Sojo Córdoba
- C28377 — Valentino Vidaurre Rodríguez

Desarrollado con [PLY](https://www.dabeaz.com/ply/).
