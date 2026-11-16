"""Cliente MCP: convierte las herramientas del servidor MCP en tools de LangChain.

Las tools que devuelve `herramientas_mcp()` se usan igual que una definida con @tool:
se le pasan al modelo con bind_tools y se ejecutan con .invoke(args).

El nombre, la descripción y los parámetros salen del propio servidor, así que no se
redefinen acá. El dato de si una tool es de lectura o escritura sale de la anotación read_only_hint del
servidor: read/ se queda con las de lectura y write/ con el resto.

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
    )


@lru_cache(maxsize=1)
def _catalogo() -> tuple[tuple[StructuredTool, bool], ...]:
    """Pide al servidor la lista de herramientas (una sola vez): (tool, es_de_lectura)."""
    return tuple((_a_tool(t), bool(t.annotations and t.annotations.read_only_hint))
                 for t in asyncio.run(_listar()))


def herramientas_mcp(solo_lectura: bool | None = None) -> list[StructuredTool]:
    """Las tools del servidor MCP. solo_lectura=True/False filtra por lectura o escritura."""
    return [t for t, lectura in _catalogo() if solo_lectura is None or lectura == solo_lectura]
