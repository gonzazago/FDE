# servidor_mcp/ — el servidor MCP propio

Expone el sistema del cliente como herramientas que cualquier agente MCP puede usar.

| Archivo | Qué hace |
|---|---|
| `server.py` | El servidor. Tiene 3 herramientas con parámetros tipados: `consultar_pedido` y `listar_pedidos_cliente` (lectura) y `reprogramar_entrega` (escritura). Las de lectura llevan `read_only_hint=True`; el agente pide aprobación para todas las demás. |
| `probar_cliente.py` | Script que lista las herramientas del servidor y llama a una. Correlo con `make mcp`. |

El agente lanza este servidor por **stdio**, no hace falta levantarlo a mano.
