from typing import Annotated

from pydantic import Field

from servidor_mcp.buscador import buscar


def buscar_documentos(
    consulta: Annotated[str, Field(description="La pregunta o los términos a buscar, en español", min_length=2)],
) -> dict:
    """Busca en las políticas de la distribuidora (devoluciones, entregas, pagos).
    Usala para preguntas sobre condiciones o reglas, no para datos de un pedido."""
    return buscar(consulta).model_dump()
