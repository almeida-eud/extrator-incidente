import re
import unicodedata

def normalizar_texto(text: str) -> str:
    if not text:
        return ""
    # remove acentos
    text = unicodedata.normalize("NFKD", text)
    text = "".join([c for c in text if not unicodedata.combining(c)])
    # converte para minúsculas
    text = text.lower()
    # remove espaços duplicados
    text = re.sub(r"\s+", " ", text)
    return text.strip()