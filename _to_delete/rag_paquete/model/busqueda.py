"""Entrada y salida de la búsqueda de documentos."""
from pydantic import BaseModel, Field


class ConsultaDocumentos(BaseModel):
    """Parámetros de `buscar_documentos`."""
    consulta: str = Field(description="La pregunta o los términos a buscar, en español")


class Fragmento(BaseModel):
    fuente: str
    texto: str
    score: int


class ResultadoBusqueda(BaseModel):
    consulta: str
    resultados: list[Fragmento]
