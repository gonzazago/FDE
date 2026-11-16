# herramientas/ — las manos

Las tools que el modelo puede pedir. Todas son tools de LangChain: se enlazan con
`bind_tools` y se ejecutan con `.invoke(args)`.

| Archivo | Qué hace |
|---|---|
| `rag.py` | **`buscar_documentos`**, definida con `@tool`. Busca en las políticas de `docs/politicas/`. Reemplazala por tu RAG de la Pre-Entrega 3 manteniendo la firma. |
| `mcp_cliente.py` | Convierte las herramientas del **servidor MCP** en tools de LangChain. Nombre, descripción y parámetros salen del servidor, no se redefinen. Si son de lectura o escritura queda en `tool.metadata`. |
| `__init__.py` | `cargar_herramientas()` junta todas, y `requiere_aprobacion(tool)` dice cuáles pasan por una persona. |

**Para sumar una tool nueva:** si es local, definila con `@tool` y agregala en `cargar_herramientas()`.
Si toca el sistema del cliente, agregala al servidor MCP y aparece sola.
