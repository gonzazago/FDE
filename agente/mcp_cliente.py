"""Cliente MCP mínimo para el agente.

Lanza el servidor por stdio, lista herramientas y llama a una.
Abre una sesión por llamada: es más lento, pero mantiene los nodos del grafo
sincrónicos y simples. En producción conviene una sesión persistente.
"""
import asyncio
import json
import sys
from dataclasses import dataclass
from functools import lru_cache

from mcp import StdioServerParameters
from mcp.client.client import Client

from config import SERVIDOR_MCP


@dataclass(frozen=True)
class HerramientaMCP:
    nombre: str
    descripcion: str
    esquema: dict
    solo_lectura: bool


def _parametros() -> StdioServerParameters:
    return StdioServerParameters(command=sys.executable, args=[str(SERVIDOR_MCP)])


async def _listar() -> list[HerramientaMCP]:
    async with Client(_parametros()) as cliente:
        res = await cliente.list_tools()
    salida = []
    for t in res.tools:
        anot = t.annotations
        solo_lectura = bool(anot and anot.read_only_hint)
        salida.append(HerramientaMCP(t.name, t.description or "", t.input_schema, solo_lectura))
    return salida


async def _llamar(nombre: str, argumentos: dict) -> dict:
    async with Client(_parametros()) as cliente:
        res = await cliente.call_tool(nombre, argumentos)
    if res.structured_content is not None:
        datos = res.structured_content
        # las funciones que devuelven dict llegan envueltas en {"result": ...} en algunos casos
        return datos.get("result", datos) if isinstance(datos, dict) and len(datos) == 1 and "result" in datos else datos
    texto = "".join(getattr(c, "text", "") for c in res.content)
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        return {"error" if res.is_error else "texto": texto}


@lru_cache(maxsize=1)
def listar_herramientas() -> tuple[HerramientaMCP, ...]:
    return tuple(asyncio.run(_listar()))


def herramienta(nombre: str) -> HerramientaMCP | None:
    return next((h for h in listar_herramientas() if h.nombre == nombre), None)


def llamar_herramienta(nombre: str, argumentos: dict) -> dict:
    return asyncio.run(_llamar(nombre, argumentos))
