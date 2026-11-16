"""Tools de LECTURA: consultan y no cambian nada. Corren sin pedir aprobación.

Todas vienen del servidor MCP (las que publica con read_only_hint=True), incluida
`buscar_documentos`, que es el RAG.
"""
from agente.tools.cliente_mcp import herramientas_mcp

LECTURA = herramientas_mcp(solo_lectura=True)
