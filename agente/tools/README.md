# agente/tools/ — las manos

Las tools que el modelo puede pedir, separadas por lo que hacen. Todas son tools de
LangChain: se enlazan con `bind_tools` y se ejecutan con `.invoke(args)`.

| Archivo | Qué hace |
|---|---|
| `read.py` | **Lectura** (no cambian nada, corren sin pausa): `buscar_documentos` (definida con `@tool`) + las tools del servidor MCP marcadas como solo lectura. Lista `LECTURA`. |
| `write.py` | **Escritura** (modifican el sistema, el grafo pide aprobación): las tools del servidor MCP que **no** son de solo lectura. Lista `ESCRITURA`. |
| `rag.py` | La búsqueda detrás de `buscar_documentos`. Reemplazala por tu RAG de la Pre-Entrega 3. |
| `mcp_cliente.py` | Convierte las tools del **servidor MCP** en tools de LangChain. Nombre, descripción y parámetros salen del servidor. |
| `__init__.py` | `TODAS` y `es_escritura(nombre)`. |

**Para sumar una tool:** si toca el sistema del cliente, agregala al servidor MCP
(`read_only_hint=True` si solo lee) y aparece sola en `LECTURA` o `ESCRITURA`, con su propio
nodo en el grafo. Si es local, definila con `@tool` en `read.py` y sumala a `LECTURA`.
