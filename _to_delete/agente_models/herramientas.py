"""Entradas y salidas de las tools."""
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


class Rechazo(BaseModel):
    """Lo que ve el modelo cuando una persona rechaza una tool de escritura."""
    rechazado: bool = True
    revisor: str | None = None
    comentario: str = ""


class ErrorHerramienta(BaseModel):
    """Lo que ve el modelo si una tool falla: el grafo no se cae, el error es un dato más."""
    ok: bool = False
    error: str
