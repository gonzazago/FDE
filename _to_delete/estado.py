"""Estado compartido: lo que viaja de nodo en nodo por el grafo."""
from typing import Annotated, TypedDict

from langchain_core.messages import HumanMessage
from langgraph.graph.message import add_messages


class EstadoAgente(TypedDict):
    mensajes: Annotated[list, add_messages]   # historial (usuario, modelo, tools); el reducer concatena
    usuario: str                              # quién habla
    pasos: int                                # vueltas del bucle en este turno
    pendiente_aprobacion: dict | None         # tool de escritura esperando a una persona
    aprobaciones: dict                        # respuesta de la persona por tool_call_id
    limite: bool                              # True si se agotaron los pasos
    traza: list[str]                          # log legible de los pasos


def entrada_turno(texto: str, usuario: str) -> dict:
    """Input para un turno nuevo: agrega el mensaje y reinicia los contadores del turno."""
    return {"mensajes": [HumanMessage(content=texto)], "usuario": usuario, "pasos": 0,
            "pendiente_aprobacion": None, "aprobaciones": {}, "limite": False, "traza": []}
