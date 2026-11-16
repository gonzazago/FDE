# ui/ — la interfaz web

Una UI al estilo de `adk web` de Google ADK. Se abre con `make ui` en http://localhost:8000.

| Archivo | Qué hace |
|---|---|
| `server.py` | Backend (FastAPI). Corre el grafo y manda cada evento (nodo o tool que arranca, nodo o tool que termina, pedido de aprobación, respuesta) al navegador en vivo con Server-Sent Events. |
| `index.html` | La página: eventos a la izquierda, chat en el centro, y el grafo con el nodo activo y el estado a la derecha. Las aprobaciones aparecen como una tarjeta con botones. |

El grafo se dibuja con Mermaid desde internet; sin conexión, el resto funciona igual.
