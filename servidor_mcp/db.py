"""Acceso a la base del sistema del cliente (SQLite)."""
import sqlite3

from config import DB_CLIENTE
from servidor_mcp.model import Pedido


def conexion() -> sqlite3.Connection:
    if not DB_CLIENTE.exists():
        raise RuntimeError("No existe la base. Corré: python sistema_cliente/seed.py")
    con = sqlite3.connect(DB_CLIENTE)
    con.row_factory = sqlite3.Row
    return con


def buscar_pedido(con: sqlite3.Connection, pedido_id: int) -> Pedido | None:
    fila = con.execute(
        """SELECT p.id, p.estado, p.fecha_entrega, p.total, c.id AS cliente_id, c.nombre AS cliente
           FROM pedidos p JOIN clientes c ON c.id = p.cliente_id WHERE p.id = ?""",
        (pedido_id,),
    ).fetchone()
    return Pedido(**fila) if fila else None
