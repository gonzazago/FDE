"""Tools de ESCRITURA: modifican el sistema del cliente. El grafo las pausa hasta que
una persona las aprueba (nodo `pedir_aprobacion`).

Salen del servidor MCP: toda tool que el servidor NO marque con read_only_hint=True cae
acá. Así una tool nueva de escritura queda protegida por defecto.
"""
from agente.tools.mcp_cliente import herramientas_mcp

ESCRITURA = [*herramientas_mcp(solo_lectura=False)]
