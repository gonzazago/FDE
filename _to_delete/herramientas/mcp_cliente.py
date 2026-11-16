"""Cliente MCP: convierte las herramientas del servidor MCP en tools de LangChain.

Las tools que devuelve `herramientas_mcp()` se usan igual que una definida con @tool:
se le pasan al modelo con bind_tools y se ejecutan con .invoke(args).

El nombre, la descripción y los parámetros salen del propio servidor, así que no se
redefinen acá. El dato `solo_lectura` (anotación read_only_hint del servidor) queda en
tool.metadata y es lo que usa el grafo para decidir si pide aprobación humana.

Nota: el adaptador oficial (langchain-mcp-adapters) todavía no soporta mcp 2.x y solo
trabaja en modo async; por eso esta versión mínima y sincrónica.
"""
import asyncio
import json
import sys
from functools import lru_cache

from langchain_core.tools import StructuredTool
from mcp import StdioServerParameters
from mcp.client.client import Client

from config import SERVIDOR_MCP


def _servidor() -> StdioServerParameters:
    return StdioServerParameters(command=sys.executable, args=[str(SERVIDOR_MCP)])


async def _listar():
    async with Client(_servidor()) as cliente:
        return (await cliente.list_tools()).tools


async def _llamar(nombre: str, argumentos: dict):
    async with Client(_servidor()) as cliente:
        res = await cliente.call_tool(nombre, argumentos)
    if res.structured_content is not None:
        datos = res.structured_content
        return datos.get("result", datos) if set(datos) == {"result"} else datos
    texto = "".join(getattr(c, "text", "") for c in res.content)
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        return {"error" if res.is_error else "texto": texto}


def _a_tool(t) -> StructuredTool:
    def ejecutar(**argumentos):
        return asyncio.run(_llamar(t.name, argumentos))

    return StructuredTool.from_function(
        func=ejecutar,
        name=t.name,
        description=t.description or "",
        args_schema=t.input_schema,  # el JSON Schema que publica el servidor
        metadata={"solo_lectura": bool(t.annotations and t.annotations.read_only_hint)},
    )


@lru_cache(maxsize=1)
def herramientas_mcp() -> tuple[StructuredTool, ...]:
    """Pide al servidor la lista de herramientas (una sola vez) y las convierte en tools."""
    return tuple(_a_tool(t) for t in asyncio.run(_listar()))
