# sistema_cliente/ — el sistema del cliente (simulado)

Hace de "sistema real" de la distribuidora para poder probar sin conectarse a nada.

| Archivo | Qué hace |
|---|---|
| `seed.py` | Crea `data/distribuidora.db` con clientes, pedidos y una tabla de auditoría, todos ficticios. Correlo con `make seed` para volver a los datos originales. |

En la Pre-Entrega 5 esto se reemplaza por un sistema legacy real, sin cambiar el servidor MCP.
