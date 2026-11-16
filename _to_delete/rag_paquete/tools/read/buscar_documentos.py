from langchain.tools import tool

from rag.buscador import buscar
from rag.model import ConsultaDocumentos


@tool(args_schema=ConsultaDocumentos)
def buscar_documentos(consulta: str) -> dict:
    """Busca en las políticas de la distribuidora (devoluciones, entregas, pagos).
    Usala para preguntas sobre condiciones o reglas, no para datos de un pedido."""
    return buscar(consulta).model_dump()
