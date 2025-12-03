import re
import csv
import os

# ============================
# GENERAR DICCIONARIO DESDE CSV
# ============================

def generar_diccionario_desde_csv(csv_path, txt_output):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"No se encontró el archivo CSV: {csv_path}")

    palabras = []

    with open(csv_path, "r", encoding="utf-8") as f:
        lector = csv.DictReader(f)
        if "Alfabético" not in lector.fieldnames:
            raise ValueError("La columna 'Alfabético' no existe en el CSV.")

        for fila in lector:
            palabra = fila.get("Alfabético", "").strip().lower()
            if palabra:
                palabras.append(palabra)

    # Quitar duplicados conservando orden y limitar a 1000
    palabras = list(dict.fromkeys(palabras))[:1000]

    with open(txt_output, "w", encoding="utf-8") as f:
        for p in palabras:
            f.write(p + "\n")

    print(f"✓ Diccionario generado con {len(palabras)} palabras.")


# ============================
# CARGA DEL DICCIONARIO
# ============================

def cargar_diccionario(ruta):
    with open(ruta, "r", encoding="utf-8") as f:
        return set(p.strip() for p in f.readlines())


# ============================
# EXPRESIONES REGULARES
# ============================

ER_PALABRA_BASICA = r'^[a-záéíóúñ]+$'
ER_PUNTUACION = r'^[\.\,\;\:\¿\?\¡\!]$'
ER_DIGITO = r'^\d+$'


# ============================
# TOKENIZADOR
# ============================

def analizar_texto(texto, diccionario):
    texto = texto.lower()

    # Separa palabras, dígitos y puntuación sin perder signos
    lexemas = re.findall(r"[a-záéíóúñ]+|[\.\,\;\:\¿\?\¡\!]|\d+", texto)

    tokens = []

    for lexema in lexemas:
        if lexema in diccionario:
            tokens.append(("PALABRA_VALIDA_ESPANOL", lexema))
        elif re.match(ER_PUNTUACION, lexema):
            tokens.append(("PUNTUACION", lexema))
        elif re.match(ER_DIGITO, lexema):
            tokens.append(("DIGITO", lexema))
        elif re.match(ER_PALABRA_BASICA, lexema):
            tokens.append(("ERROR_ORTOGRAFICO", lexema))
        else:
            tokens.append(("ERROR_ORTOGRAFICO", lexema))

    return tokens


# ============================
# GUARDAR SALIDA
# ============================

def guardar_salida(tokens, ruta):
    with open(ruta, "w", encoding="utf-8") as f:
        for tipo, lexema in tokens:
            f.write(f"{tipo} {lexema}\n")


# ============================
# MAIN
# ============================

if __name__ == "__main__":
    # 1. Generar diccionario desde CSV
    generar_diccionario_desde_csv("diccionario_espanol.csv", "diccionario_espanol.txt")

    # 2. Cargar diccionario en memoria
    diccionario = cargar_diccionario("diccionario_espanol.txt")

    # 3. Leer texto de entrada
    with open("texto_entrada.txt", "r", encoding="utf-8") as f:
        texto = f.read()

    # 4. Analizar
    tokens = analizar_texto(texto, diccionario)

    # 5. Guardar salida
    guardar_salida(tokens, "tokens_salida.txt")

    print("✓ Análisis completado. Revisa tokens_salida.txt")
