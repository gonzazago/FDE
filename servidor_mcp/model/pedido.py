"""Pedidos y resultados de las tools."""
from pydantic import BaseModel


class Pedido(BaseModel):
    id: int
    estado: str
    fecha_entrega: str
    total: float
    cliente_id: int
    cliente: str


class PedidoEncontrado(Pedido):
    encontrado: bool = True


class PedidoInexistente(BaseModel):
    encontrado: bool = False
    pedido_id: int


class ResumenPedido(BaseModel):
    id: int
    estado: str
    fecha_entrega: str


class PedidosCliente(BaseModel):
    cliente_id: int
    pedidos: list[ResumenPedido]


class ResultadoReprogramacion(BaseModel):
    ok: bool = True
    pedido_id: int
    fecha_anterior: str
    fecha_nueva: str


class ErrorOperacion(BaseModel):
    ok: bool = False
    error: str
