# scanner_core.py
# Lógica del analizador: tokenización, expresiones y clasificación

import re
from utlis import normalizar_palabra


# Expresiones regulares
# ER_PALABRA_BASICA: solo letras (Unicode) -> usamos clase Unicode
ER_PALABRA_BASICA = r'^[^\W\d_]+$'     # letras unicode (sin dígitos ni underscore)
ER_PUNTUACION = r'^[\.\,\;\:\¿\?\¡\!]$'
ER_DIGITO = r'^\d+(?:\.\d+)?$'         # acepta enteros y decimales

# Token pattern: letras (Unicode), números (enteros/decimales), signos de puntuación, fallback
TOKEN_PATTERN = re.compile(r"[^\W\d_]+|\d+(?:\.\d+)?|[.,;:¿\?¡!]|[^\s]", flags=re.UNICODE)

def analizar_texto(texto: str, diccionario: set):
    """
    Analiza el texto y devuelve lista de tuplas (TIPO, lexema).
    Prioridad:
      1) diccionario -> PALABRA_VALIDA_ESPANOL
      2) puntuación  -> PUNTUACION
      3) dígito      -> DIGITO
      4) palabra (letras) -> ERROR_ORTOGRAFICO
      5) fallback -> ERROR_ORTOGRAFICO
    """
    if texto is None:
        texto = ""
    lexemas = TOKEN_PATTERN.findall(texto)
    tokens = []
    for lex in lexemas:
        lex_norm = normalizar_palabra(lex)
        if lex_norm and lex_norm in diccionario:
            tokens.append(("PALABRA_VALIDA_ESPANOL", lex))
            continue
        if re.match(ER_PUNTUACION, lex):
            tokens.append(("PUNTUACION", lex))
            continue
        if re.match(ER_DIGITO, lex):
            tokens.append(("DIGITO", lex))
            continue
        if lex_norm and re.match(ER_PALABRA_BASICA, lex_norm):
            tokens.append(("ERROR_ORTOGRAFICO", lex))
            continue
        # cualquier otro caso
        tokens.append(("ERROR_ORTOGRAFICO", lex))
    return tokens
