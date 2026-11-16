"""Modelos pydantic del servidor: la forma de lo que devuelven las tools."""
from servidor_mcp.model.busqueda import Fragmento, ResultadoBusqueda
from servidor_mcp.model.pedido import (
    ErrorOperacion, Pedido, PedidoEncontrado, PedidoInexistente, PedidosCliente,
    ResultadoReprogramacion, ResumenPedido,
)

__all__ = ["Pedido", "PedidoEncontrado", "PedidoInexistente", "ResumenPedido", "PedidosCliente",
           "ResultadoReprogramacion", "ErrorOperacion", "Fragmento", "ResultadoBusqueda"]
