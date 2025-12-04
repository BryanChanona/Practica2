# utils.py
# Utilidades: normalización Unicode y helpers

import unicodedata

def normalizar_palabra(s: str) -> str:
    """
    Normaliza una palabra para comparación:
    - elimina BOM y NBSP
    - strip
    - Unicode NFC
    - retorna en minúsculas
    """
    if s is None:
        return ""
    s = s.replace("\ufeff", "").replace("\u00A0", " ")
    s = s.strip()
    if not s:
        return ""
    s = unicodedata.normalize("NFC", s)
    return s.lower()
