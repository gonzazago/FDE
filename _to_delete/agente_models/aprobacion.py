"""Lo que se le pide a la persona que supervisa y lo que ella responde."""
from typing import Literal

from pydantic import BaseModel, Field


class SolicitudAprobacion(BaseModel):
    """Payload del `interrupt`: qué quiere hacer el agente y por qué."""
    tipo: Literal["aprobacion"] = "aprobacion"
    usuario: str
    herramienta: str
    argumentos: dict = Field(default_factory=dict)
    razon: str = ""
    tool_call_id: str = ""


class DecisionAprobacion(BaseModel):
    """Lo que devuelve la persona al reanudar el grafo (`Command(resume=...)`)."""
    aprobado: bool
    revisor: str = "revisor"
    comentario: str = ""
