from typing import Annotated

from pydantic import Field

from servidor_mcp.db import conexion
from servidor_mcp.model import PedidosCliente, ResumenPedido


def listar_pedidos_cliente(
    cliente_id: Annotated[int, Field(description="ID numérico del cliente, por ejemplo 12", gt=0)],
) -> dict:
    """Lista todos los pedidos de un cliente (id, estado y fecha de entrega).
    Usala cuando el usuario pregunta por 'mis pedidos' o los pedidos de un cliente."""
    with conexion() as con:
        filas = con.execute(
            "SELECT id, estado, fecha_entrega FROM pedidos WHERE cliente_id = ? ORDER BY id",
            (cliente_id,),
        ).fetchall()
    return PedidosCliente(cliente_id=cliente_id, pedidos=[ResumenPedido(**f) for f in filas]).model_dump()
