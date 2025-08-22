# Tarea programada 1 Avance 5

Para esta etapa ahora el parser y el lexer se corren al ejecutar la interfaz, además en la funcionalidad de importar, al agregar otro archivo diferente al de la profesora, la sección de Error report hay que darle al botón nuevamente de Get report para que dé el nuevo análisis del otro archivo, mientras que en la sección de grápico se refresca automáticamente.


## Pasos para construir el proyecto:

- En la terminal hay que posicionarse en la carpeta ` avance5 `.

- Tener instalado Python 3.

- Importar las librerías de Python que no vienen por defecto:
    - En algunos sistemas Linux, tkinter puede no estar instalado por defecto, entonces usa este comando ` sudo apt install python3-tk `.
    - Instalar Matplotlib en la terminal con el comando: ` pip install matplotlib `.
    - Instalar Seaborn con el comando en la terminal ` pip install seaborn `.
    - Instalar Pillow (PIL) con ` pip install pillow `.
    - Instalar Ply con ` pip install ply `.


## Comando para ejecutar:

- Para correr la GUI: ` python3 interface.py ` (esto ejecuta también automáticamente el parser y el lexer)

- Para correr el lexer: ` python3 Lexer.py `

- Para correr el parser: ` python3 parser.py `