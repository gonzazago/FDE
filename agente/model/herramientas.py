"""Lo que ve el modelo cuando una tool se rechaza o falla."""
from pydantic import BaseModel


class Rechazo(BaseModel):
    """Lo que ve el modelo cuando una persona rechaza una tool de escritura."""
    rechazado: bool = True
    revisor: str | None = None
    comentario: str = ""


class ErrorHerramienta(BaseModel):
    """Lo que ve el modelo si una tool falla: el grafo no se cae, el error es un dato más."""
    ok: bool = False
    error: str
