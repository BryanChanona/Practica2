# app.py
# Punto de entrada - lanza GUI por defecto o CLI con --cli

import sys
import os
from scanner_io import cargar_diccionario, generar_diccionario_desde_csv, guardar_salida
from scanner_core import analizar_texto
from gui import AnalizadorGUI

def main_cli_example():
    csv_path = "diccionario_espanol.csv"
    if os.path.exists(csv_path) and not os.path.exists("diccionario_espanol.txt"):
        try:
            generar_diccionario_desde_csv(csv_path, "diccionario_espanol.txt")
            print("Diccionario generado desde CSV.")
        except Exception as e:
            print("Advertencia al generar diccionario:", e)

    if os.path.exists("diccionario_espanol.txt"):
        diccionario = cargar_diccionario("diccionario_espanol.txt")
    else:
        diccionario = set()

    if not os.path.exists("texto_entrada.txt"):
        print("No se encontró texto_entrada.txt. Crea ese archivo o usa la GUI.")
        return

    with open("texto_entrada.txt", "r", encoding="utf-8") as f:
        texto = f.read()

    tokens = analizar_texto(texto, diccionario)
    guardar_salida(tokens, "tokens_salida.txt")
    print("Análisis completado (modo CLI). tokens_salida.txt creado.")

if __name__ == "__main__":
    if "--cli" in sys.argv:
        main_cli_example()
    else:
        app = AnalizadorGUI()
        app.mainloop()
