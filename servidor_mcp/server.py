"""Servidor MCP de la Distribuidora Los Andes (sistema simulado en SQLite).

Publica las tools de tools/read (lectura, read_only_hint=True) y tools/write (escritura,
read_only_hint=False) y 1 resource de solo lectura (clientes://lista). El agente usa
esa anotación para decidir cuándo pausar y pedir aprobación humana.

Transporte: stdio (el agente lanza este proceso).  Uso manual:
    python servidor_mcp/server.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mcp.server.mcpserver import MCPServer  # noqa: E402  (mcp >= 2; antes: FastMCP)
from mcp.types import ToolAnnotations  # noqa: E402

from servidor_mcp.db import conexion  # noqa: E402
from servidor_mcp.tools import ESCRITURA, LECTURA  # noqa: E402

servidor = MCPServer(
    name="distribuidora-los-andes",
    instructions="Consulta y gestión de pedidos mayoristas de la Distribuidora Los Andes.",
)

for funcion in LECTURA:
    servidor.tool(title=funcion.__name__.replace("_", " ").capitalize(),
                  annotations=ToolAnnotations(read_only_hint=True))(funcion)
for funcion in ESCRITURA:
    servidor.tool(title=funcion.__name__.replace("_", " ").capitalize(),
                  annotations=ToolAnnotations(read_only_hint=False, destructive_hint=False,
                                              idempotent_hint=True))(funcion)


@servidor.resource("clientes://lista", title="Clientes", mime_type="application/json")
def clientes() -> list[dict]:
    """Resource de solo lectura: los clientes de la distribuidora."""
    with conexion() as con:
        return [dict(f) for f in con.execute("SELECT * FROM clientes").fetchall()]


if __name__ == "__main__":
    servidor.run("stdio")
