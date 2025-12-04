# scanner_io.py
# I/O del proyecto: generación y carga de diccionario, guardado de salida

import csv
import os
from utlis import normalizar_palabra


def generar_diccionario_desde_csv(csv_path, txt_output, max_words=1000):
    """
    Genera diccionario a partir del CSV con columna "Alfabético".
    Guarda un .txt con una palabra por línea (normalizadas).
    Retorna el número de palabras escritas.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"No se encontró el archivo CSV: {csv_path}")

    palabras = []
    with open(csv_path, "r", encoding="utf-8") as f:
        lector = csv.DictReader(f)
        if "Alfabético" not in lector.fieldnames:
            raise ValueError("La columna 'Alfabético' no existe en el CSV.")
        for fila in lector:
            palabra = fila.get("Alfabético", "")
            if palabra is None:
                continue
            palabra_norm = normalizar_palabra(palabra)
            if palabra_norm:
                palabras.append(palabra_norm)

    # Eliminar duplicados preservando orden y limitar
    palabras = list(dict.fromkeys(palabras))[:max_words]

    with open(txt_output, "w", encoding="utf-8") as f:
        for p in palabras:
            f.write(p + "\n")

    return len(palabras)


def cargar_diccionario(ruta):
    """
    Carga un diccionario (.txt) y devuelve un set de palabras normalizadas.
    """
    palabras = set()
    with open(ruta, "r", encoding="utf-8") as f:
        for linea in f:
            p = linea.rstrip("\n").strip()
            if not p:
                continue
            p_norm = normalizar_palabra(p)
            if p_norm:
                palabras.add(p_norm)
    return palabras


def guardar_salida(tokens, ruta):
    """
    Guarda tokens en formato 'TIPO LEXEMA' por línea.
    """
    with open(ruta, "w", encoding="utf-8") as f:
        for tipo, lexema in tokens:
            f.write(f"{tipo} {lexema}\n")
