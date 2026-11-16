from typing import Annotated

from pydantic import Field

from servidor_mcp.db import buscar_pedido, conexion
from servidor_mcp.model import PedidoEncontrado, PedidoInexistente


def consultar_pedido(
    pedido_id: Annotated[int, Field(description="Número de pedido, por ejemplo 1042", gt=0)],
) -> dict:
    """Devuelve estado, fecha de entrega, total y cliente de UN pedido.
    Usala cuando el usuario pregunta por un pedido puntual con su número."""
    with conexion() as con:
        pedido = buscar_pedido(con, pedido_id)
    if pedido is None:
        return PedidoInexistente(pedido_id=pedido_id).model_dump()
    return PedidoEncontrado(**pedido.model_dump()).model_dump()
