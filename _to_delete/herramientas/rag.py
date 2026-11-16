"""buscar_documentos: versión simplificada del RAG de la Pre-Entrega 3.

Acá se busca por coincidencia de palabras sobre los .md de docs/politicas para
que el proyecto corra sin dependencias extra. Reemplazá `buscar_documentos`
por tu RAG real (búsqueda híbrida + permisos); el grafo no cambia mientras
respetes la misma firma y el mismo formato de salida.
"""
import re
import unicodedata

from langchain.tools import tool

from config import DOCS_POLITICAS

STOPWORDS = {
    "de", "la", "el", "los", "las", "un", "una", "y", "o", "a", "en", "que", "se", "por", "con",
    "para", "del", "al", "es", "su", "sus", "me", "mi", "qué", "cual", "cuál", "como", "cómo",
    "sobre", "dice", "politica", "política", "hay", "puedo", "tengo",
}


def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def _tokens(texto: str) -> set[str]:
    palabras = re.findall(r"[a-z0-9]+", _normalizar(texto))
    # recorte simple de plurales/derivados: "devoluciones" ~ "devolver" -> "devol"
    return {p[:5] for p in palabras if p not in {_normalizar(s) for s in STOPWORDS} and len(p) > 2}


def _fragmentos():
    for archivo in sorted(DOCS_POLITICAS.glob("*.md")):
        for linea in archivo.read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if linea and not linea.startswith("#"):
                yield archivo.stem, linea


@tool
def buscar_documentos(consulta: str) -> dict:
    """Busca en las políticas de la distribuidora (devoluciones, entregas, pagos).
    Usala para preguntas sobre condiciones o reglas, no para datos de un pedido.

    Args:
        consulta: La pregunta o los términos a buscar, en español
    """
    k, umbral = 3, 1
    q = _tokens(consulta)
    puntuados = []
    for fuente, texto in _fragmentos():
        score = len(q & _tokens(texto))
        if score >= umbral:
            puntuados.append((score, fuente, texto))
    puntuados.sort(key=lambda x: -x[0])
    return {
        "consulta": consulta,
        "resultados": [{"fuente": f, "texto": t, "score": s} for s, f, t in puntuados[:k]],
    }


buscar_documentos.metadata = {"solo_lectura": True}
