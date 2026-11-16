"""Búsqueda sobre las políticas: versión simplificada del RAG de la Pre-Entrega 3.

Busca por coincidencia de palabras en los .md de docs/politicas para que el proyecto corra
sin dependencias extra. Reemplazá `buscar` por tu RAG real (búsqueda híbrida + permisos):
el grafo no cambia mientras `buscar_documentos` (en read.py) siga devolviendo lo mismo.
"""
import re
import unicodedata

from agente.models import Fragmento, ResultadoBusqueda
from config import DOCS_POLITICAS

STOPWORDS = {
    "de", "la", "el", "los", "las", "un", "una", "y", "o", "a", "en", "que", "se", "por", "con",
    "para", "del", "al", "es", "su", "sus", "me", "mi", "qué", "cual", "cuál", "como", "cómo",
    "sobre", "dice", "politica", "política", "hay", "puedo", "tengo",
}


def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


_STOP = {_normalizar(s) for s in STOPWORDS}


def _tokens(texto: str) -> set[str]:
    palabras = re.findall(r"[a-z0-9]+", _normalizar(texto))
    # recorte simple de plurales/derivados: "devoluciones" ~ "devolver" -> "devol"
    return {p[:5] for p in palabras if p not in _STOP and len(p) > 2}


def _fragmentos():
    for archivo in sorted(DOCS_POLITICAS.glob("*.md")):
        for linea in archivo.read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if linea and not linea.startswith("#"):
                yield archivo.stem, linea


def buscar(consulta: str, k: int = 3) -> ResultadoBusqueda:
    q = _tokens(consulta)
    puntuados = [(len(q & _tokens(t)), f, t) for f, t in _fragmentos()]
    mejores = sorted((p for p in puntuados if p[0] >= 1), key=lambda p: -p[0])[:k]
    return ResultadoBusqueda(consulta=consulta,
                             resultados=[Fragmento(fuente=f, texto=t, score=s) for s, f, t in mejores])
