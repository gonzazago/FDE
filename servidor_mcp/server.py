"""Servidor MCP de la Distribuidora Los Andes (sistema simulado en SQLite).

Expone 3 herramientas con parámetros tipados:
  - consultar_pedido        (lectura)
  - listar_pedidos_cliente  (lectura)
  - reprogramar_entrega     (ESCRITURA -> el agente pide aprobación humana)
y 1 resource de solo lectura (clientes://lista).

Las anotaciones `read_only_hint` le dicen al agente qué herramientas modifican
el sistema. El agente usa ese dato para decidir cuándo pausar y pedir permiso.

Transporte: stdio (el agente lanza este proceso).  Uso manual:
    python servidor_mcp/server.py
"""
import sqlite3
import sys
from datetime import date
from pathlib import Path
from typing import Annotated

from pydantic import Field

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import DB_CLIENTE  # noqa: E402

from mcp.server.mcpserver import MCPServer  # mcp >= 2 (antes: FastMCP)
from mcp.types import ToolAnnotations

servidor = MCPServer(
    name="distribuidora-los-andes",
    instructions="Consulta y gestión de pedidos mayoristas de la Distribuidora Los Andes.",
)

ESTADOS_NO_REPROGRAMABLES = {"entregado", "cancelado"}


def _conexion() -> sqlite3.Connection:
    if not DB_CLIENTE.exists():
        raise RuntimeError("No existe la base. Corré: python sistema_cliente/seed.py")
    con = sqlite3.connect(DB_CLIENTE)
    con.row_factory = sqlite3.Row
    return con


def _pedido(con: sqlite3.Connection, pedido_id: int) -> dict | None:
    fila = con.execute(
        """SELECT p.id, p.estado, p.fecha_entrega, p.total, c.id AS cliente_id, c.nombre AS cliente
           FROM pedidos p JOIN clientes c ON c.id = p.cliente_id WHERE p.id = ?""",
        (pedido_id,),
    ).fetchone()
    return dict(fila) if fila else None


@servidor.tool(
    title="Consultar pedido",
    annotations=ToolAnnotations(read_only_hint=True),
)
def consultar_pedido(
    pedido_id: Annotated[int, Field(description="Número de pedido, por ejemplo 1042", gt=0)],
) -> dict:
    """Devuelve estado, fecha de entrega, total y cliente de UN pedido.
    Usala cuando el usuario pregunta por un pedido puntual con su número."""
    with _conexion() as con:
        pedido = _pedido(con, pedido_id)
    if pedido is None:
        return {"encontrado": False, "pedido_id": pedido_id}
    return {"encontrado": True, **pedido}


@servidor.tool(
    title="Listar pedidos de un cliente",
    annotations=ToolAnnotations(read_only_hint=True),
)
def listar_pedidos_cliente(
    cliente_id: Annotated[int, Field(description="ID numérico del cliente, por ejemplo 12", gt=0)],
) -> dict:
    """Lista todos los pedidos de un cliente (id, estado y fecha de entrega).
    Usala cuando el usuario pregunta por 'mis pedidos' o los pedidos de un cliente."""
    with _conexion() as con:
        filas = con.execute(
            "SELECT id, estado, fecha_entrega FROM pedidos WHERE cliente_id = ? ORDER BY id",
            (cliente_id,),
        ).fetchall()
    return {"cliente_id": cliente_id, "pedidos": [dict(f) for f in filas]}


@servidor.tool(
    title="Reprogramar entrega",
    annotations=ToolAnnotations(read_only_hint=False, destructive_hint=False, idempotent_hint=True),
)
def reprogramar_entrega(
    pedido_id: Annotated[int, Field(description="Número de pedido a reprogramar", gt=0)],
    nueva_fecha: Annotated[date, Field(description="Nueva fecha de entrega en formato AAAA-MM-DD")],
    motivo: Annotated[str, Field(description="Motivo informado por el cliente", min_length=3, max_length=200)],
) -> dict:
    """MODIFICA el sistema: cambia la fecha de entrega de un pedido y deja registro en auditoría.
    Solo para pedidos que todavía no fueron entregados y con una fecha futura."""
    if nueva_fecha <= date.today():
        return {"ok": False, "error": "La nueva fecha tiene que ser posterior a hoy."}
    with _conexion() as con:
        pedido = _pedido(con, pedido_id)
        if pedido is None:
            return {"ok": False, "error": f"No existe el pedido {pedido_id}."}
        if pedido["estado"] in ESTADOS_NO_REPROGRAMABLES:
            return {"ok": False, "error": f"El pedido está {pedido['estado']} y no se puede reprogramar."}
        con.execute("UPDATE pedidos SET fecha_entrega = ? WHERE id = ?", (nueva_fecha.isoformat(), pedido_id))
        con.execute(
            "INSERT INTO auditoria (pedido_id, accion, detalle) VALUES (?, ?, ?)",
            (pedido_id, "reprogramar_entrega",
             f"{pedido['fecha_entrega']} -> {nueva_fecha.isoformat()} | {motivo}"),
        )
    return {"ok": True, "pedido_id": pedido_id, "fecha_anterior": pedido["fecha_entrega"],
            "fecha_nueva": nueva_fecha.isoformat()}


@servidor.resource("clientes://lista", title="Clientes", mime_type="application/json")
def clientes() -> list[dict]:
    """Resource de solo lectura: los clientes de la distribuidora."""
    with _conexion() as con:
        return [dict(f) for f in con.execute("SELECT * FROM clientes").fetchall()]


if __name__ == "__main__":
    servidor.run("stdio")
