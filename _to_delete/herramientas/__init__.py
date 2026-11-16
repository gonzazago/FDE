"""Todas las tools que puede usar el agente."""
from herramientas.mcp_cliente import herramientas_mcp
from herramientas.rag import buscar_documentos


def cargar_herramientas() -> list:
    """buscar_documentos (definida con @tool) + las herramientas del servidor MCP."""
    return [buscar_documentos, *herramientas_mcp()]


def requiere_aprobacion(tool) -> bool:
    """Toda tool que no esté marcada como de solo lectura pasa por una persona."""
    return not (tool.metadata or {}).get("solo_lectura", False)
