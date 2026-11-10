"""Estado compartido del grafo y esquema de decisión (validado con Pydantic)."""
from typing import Annotated, Any, Literal, TypedDict

from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


class EstadoAgente(TypedDict):
    # Pedidos por la consigna:
    mensajes: Annotated[list, add_messages]   # reducer: concatena, no pisa
    usuario: str                              # quién habla (para auditoría / permisos)
    pasos: int                                # vueltas del bucle decidir -> ejecutar en este turno
    pendiente_aprobacion: dict | None         # acción de escritura esperando a una persona
    # Auxiliares (se reinician en cada turno):
    decision: dict | None                     # última decisión del nodo decidir
    resultados: list[dict]                    # salidas de herramientas de este turno
    traza: list[str]                          # log legible de los pasos


class Decision(BaseModel):
    """Salida del nodo decidir. Si el LLM devuelve otra cosa, falla la validación
    y el grafo responde en lugar de romperse (error común nº 3 de la unidad)."""

    accion: Literal["buscar_documentos", "usar_herramienta", "responder"]
    herramienta: str | None = Field(None, description="Nombre exacto de la herramienta MCP si accion=usar_herramienta")
    argumentos: dict[str, Any] = Field(default_factory=dict)
    razon: str = Field(description="Por qué se eligió esta acción, en una oración")


def entrada_turno(texto: str, usuario: str) -> dict:
    """Input para arrancar un turno nuevo en un thread (reinicia contadores del turno)."""
    from langchain_core.messages import HumanMessage

    return {
        "mensajes": [HumanMessage(content=texto)],
        "usuario": usuario,
        "pasos": 0,
        "pendiente_aprobacion": None,
        "decision": None,
        "resultados": [],
        "traza": [],
    }
