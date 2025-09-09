# Lexer Compiladores

Este proyecto implementa un analizador léxico (lexer) para una variante de Python, usando [PLY](https://www.dabeaz.com/ply/) como motor de análisis léxico.

## Estructura del proyecto

- [`Lexer.py`](Lexer.py): Implementación principal del lexer, incluyendo reglas de tokens, manejo de indentación, errores y pruebas.
- [`symbol_table.py`](symbol_table.py): Implementa una tabla de símbolos simple para el análisis léxico.
- [`utils.py`](utils.py): Utilidades para el manejo y reporte de errores.
- [`test.py`](test.py): Archivo de prueba con casos diseñados para estresar el lexer.
- [`Lexer_report.txt`](Lexer_report.txt): Salida generada por el lexer al analizar `test.py`.
- [`requirements.txt`](requirements.txt): Dependencias necesarias para ejecutar el proyecto.

## Instalación

1. Clona el repositorio.
2. Instala las dependencias:
   ```sh
   pip install -r requirements.txt
   ```

## Uso

Para ejecutar el lexer sobre el archivo de prueba y generar el reporte:

```sh
python Lexer.py
```

Esto analizará `test.py` y generará el archivo `Lexer_report.txt` con los tokens y errores detectados.

## Personalización

- Puedes modificar [`test.py`](test.py) para agregar tus propios casos de prueba.
- El lexer está diseñado para detectar errores de indentación, uso de punto y coma, caracteres ilegales, y otros detalles sintácticos.

## Créditos

Desarrollado usando PLY
