"""El estado compartido del grafo, como modelo pydantic: lo que viaja de nodo en nodo."""
from typing import Annotated

from langchain_core.messages import AnyMessage, HumanMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

REINICIAR = "__reiniciar__"  # marca para vaciar la traza al empezar un turno nuevo


def acumular_traza(actual: list[str], nuevas: list[str]) -> list[str]:
    """Reducer: cada nodo agrega sus líneas (así varias tools en paralelo no se pisan)."""
    if nuevas and nuevas[0] == REINICIAR:
        return nuevas[1:]
    return [*actual, *nuevas]


class EstadoAgente(BaseModel):
    mensajes: Annotated[list[AnyMessage], add_messages] = Field(default_factory=list)  # historial
    usuario: str = ""                      # quién habla
    pasos: int = 0                         # vueltas del bucle en este turno
    pendiente_aprobacion: dict | None = None   # tool de escritura esperando a una persona
    aprobaciones: dict[str, dict] = Field(default_factory=dict)  # decisión humana por tool_call_id
    limite: bool = False                   # True si se agotaron los pasos
    traza: Annotated[list[str], acumular_traza] = Field(default_factory=list)  # log legible


def entrada_turno(texto: str, usuario: str) -> dict:
    """Input para un turno nuevo: agrega el mensaje y reinicia los contadores del turno."""
    return {"mensajes": [HumanMessage(content=texto)], "usuario": usuario, "pasos": 0,
            "pendiente_aprobacion": None, "aprobaciones": {}, "limite": False, "traza": [REINICIAR]}
