"""Tools de LECTURA del servidor: no cambian nada (se publican con read_only_hint=True)."""
from servidor_mcp.tools.read.buscar_documentos import buscar_documentos
from servidor_mcp.tools.read.consultar_pedido import consultar_pedido
from servidor_mcp.tools.read.listar_pedidos_cliente import listar_pedidos_cliente

LECTURA = [buscar_documentos, consultar_pedido, listar_pedidos_cliente]
