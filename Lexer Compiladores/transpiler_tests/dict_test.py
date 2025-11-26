# diccionario básico
edades = {"Ana": 20, "Luis": 22}

# "agregar" (equivalente a append en espíritu)
edades["Milton"] = 21  # mete una nueva clave-valor
edades["Ana"] = 21  # actualiza una clave existente

# acceder
print(edades["Luis"])  # 22

# no hay sublist/slice en dict

# "remove" pero por clave (no por índice)
del edades["Luis"]

print(edades)  # {'Ana': 21, 'Milton': 21}
