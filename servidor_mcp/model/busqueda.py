"""Resultado de la búsqueda de documentos."""
from pydantic import BaseModel


class Fragmento(BaseModel):
    fuente: str
    texto: str
    score: int


class ResultadoBusqueda(BaseModel):
    consulta: str
    resultados: list[Fragmento]
