"""Tools de LECTURA: consultan y no cambian nada. Corren sin pedir aprobación."""
from langchain.tools import tool

from agente.models import ConsultaDocumentos
from agente.tools import rag
from agente.tools.mcp_cliente import herramientas_mcp


@tool(args_schema=ConsultaDocumentos)
def buscar_documentos(consulta: str) -> dict:
    """Busca en las políticas de la distribuidora (devoluciones, entregas, pagos).
    Usala para preguntas sobre condiciones o reglas, no para datos de un pedido."""
    return rag.buscar(consulta).model_dump()


# buscar_documentos (local, con @tool) + las tools del servidor MCP marcadas como solo lectura
LECTURA = [buscar_documentos, *herramientas_mcp(solo_lectura=True)]
