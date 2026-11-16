from datetime import date
from typing import Annotated

from pydantic import Field

from servidor_mcp.db import buscar_pedido, conexion
from servidor_mcp.model import ErrorOperacion, ResultadoReprogramacion

ESTADOS_NO_REPROGRAMABLES = {"entregado", "cancelado"}


def reprogramar_entrega(
    pedido_id: Annotated[int, Field(description="Número de pedido a reprogramar", gt=0)],
    nueva_fecha: Annotated[date, Field(description="Nueva fecha de entrega en formato AAAA-MM-DD")],
    motivo: Annotated[str, Field(description="Motivo informado por el cliente", min_length=3, max_length=200)],
) -> dict:
    """MODIFICA el sistema: cambia la fecha de entrega de un pedido y deja registro en auditoría.
    Solo para pedidos que todavía no fueron entregados y con una fecha futura."""
    if nueva_fecha <= date.today():
        return ErrorOperacion(error="La nueva fecha tiene que ser posterior a hoy.").model_dump()
    with conexion() as con:
        pedido = buscar_pedido(con, pedido_id)
        if pedido is None:
            return ErrorOperacion(error=f"No existe el pedido {pedido_id}.").model_dump()
        if pedido.estado in ESTADOS_NO_REPROGRAMABLES:
            return ErrorOperacion(error=f"El pedido está {pedido.estado} y no se puede reprogramar.").model_dump()
        con.execute("UPDATE pedidos SET fecha_entrega = ? WHERE id = ?", (nueva_fecha.isoformat(), pedido_id))
        con.execute(
            "INSERT INTO auditoria (pedido_id, accion, detalle) VALUES (?, ?, ?)",
            (pedido_id, "reprogramar_entrega",
             f"{pedido.fecha_entrega} -> {nueva_fecha.isoformat()} | {motivo}"),
        )
    return ResultadoReprogramacion(pedido_id=pedido_id, fecha_anterior=pedido.fecha_entrega,
                                   fecha_nueva=nueva_fecha.isoformat()).model_dump()
