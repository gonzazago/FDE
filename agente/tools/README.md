# agente/tools/ — las manos

Las tools que el modelo puede pedir, separadas por lo que hacen. Todas son tools de
LangChain: se enlazan con `bind_tools` y se ejecutan con `.invoke(args)`.

| Carpeta o archivo | Qué hace |
|---|---|
| `read/` | **Lectura** (no cambian nada, corren sin pausa). `__init__.py` arma la lista `LECTURA` con las tools de solo lectura del servidor MCP, incluida `buscar_documentos` (el RAG). |
| `write/` | **Escritura** (modifican el sistema, el grafo pide aprobación). `__init__.py` arma la lista `ESCRITURA`: las tools del servidor MCP que **no** son de solo lectura. |
| `cliente_mcp.py` | Convierte las tools del **servidor MCP** en tools de LangChain. Nombre, descripción y parámetros salen del servidor. |
| `__init__.py` | `TODAS` y `es_escritura(nombre)`. |

**Para sumar una tool:** si toca el sistema del cliente, agregala al servidor MCP
(`read_only_hint=True` si solo lee) y aparece sola en `read/` o `write/`, con su propio nodo
en el grafo. Si preferís una tool local, definila con `@tool` y sumala a `LECTURA`.
